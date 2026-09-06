from __future__ import annotations
from collections import defaultdict
from statistics import mean
from datetime import date
from models import RouteBasketItem, IndexPoint, LeadTimePoint, HeatmapItem
from data.dgca_route_basket import load_verified_basket

class AirfareIndexEngine:
    def __init__(self, records:list[dict], routes=None, base_period="2024-01"):
        self.records=records; self.routes=load_verified_basket() if routes is None else routes; self.base_period=base_period
    def route_basket(self):
        by=defaultdict(list)
        for r in self.records:
            if r.get('total_fare') and r.get('collection_status','SUCCESS')=='SUCCESS':by[f"{r.get('origin')}-{r.get('destination')}"].append(float(r['total_fare']))
        return [RouteBasketItem(route_id=r.route_id,origin=r.origin,destination=r.destination,origin_name=r.origin_name,destination_name=r.destination_name,passenger_traffic_annual=None,traffic_share=round(r.dgca_traffic_weight*100,3),weight=round(r.dgca_traffic_weight,6),total_observations=len(by[r.route_id]),avg_fare=round(mean(by[r.route_id]),2) if by[r.route_id] else 0,weight_status=r.weight_status) for r in self.routes]
    def _daily_route(self):
        d=defaultdict(lambda:defaultdict(list))
        for r in self.records:
            if r.get('collection_status','SUCCESS')!='SUCCESS' or not r.get('total_fare'):continue
            if r.get('availability_status','AVAILABLE') in ('SOLD_OUT','CANCELLED'):continue
            day=str(r.get('observation_timestamp') or r.get('collected_at'))[:10]
            rid=r.get('route_id') or f"{r.get('origin')}-{r.get('destination')}"
            d[day][rid].append(float(r['total_fare']))
        return d
    def calculate_index_series(self):
        daily=self._daily_route(); dates=sorted(daily)
        if not dates:return []
        weights={r.route_id:r.dgca_traffic_weight for r in self.routes}
        base_date=next((d for d in dates if d.startswith(self.base_period[:7])),dates[0])
        def agg(day):
            pairs=[(weights[rid],mean(vals)) for rid,vals in daily[day].items() if rid in weights and vals]
            if not pairs:return None
            tw=sum(w for w,_ in pairs);return sum(w*v for w,v in pairs)/tw
        base_val=agg(base_date) or agg(dates[0])
        out=[]
        for d in dates:
            cur=agg(d)
            if cur is None:continue
            idx=cur/base_val*100
            prior=out[-1].index_value if out else 100
            seven=next((x.index_value for x in reversed(out) if (date.fromisoformat(d)-date.fromisoformat(x.period)).days>=7),out[0].index_value if out else 100)
            thirty=next((x.index_value for x in reversed(out) if (date.fromisoformat(d)-date.fromisoformat(x.period)).days>=30),out[0].index_value if out else 100)
            out.append(IndexPoint(period=d,index_value=round(idx,2),base_period=base_date,base_index=100,daily_change_pct=round((idx-prior)/prior*100,2) if prior else 0,weekly_change_pct=round((idx-seven)/seven*100,2) if seven else 0,monthly_change_pct=round((idx-thirty)/thirty*100,2) if thirty else 0,total_routes=len(weights),total_observations=sum(len(v) for v in daily[d].values()),methodology_version="2.0"))
        return out
    def lead_time_curve(self,route_id=None):
        by=defaultdict(list)
        for r in self.records:
            rid=r.get('route_id') or f"{r.get('origin')}-{r.get('destination')}"
            if route_id and rid!=route_id:continue
            if r.get('total_fare') and r.get('lead_time_days',r.get('lead_time')) in (1,7,15,30,45):by[r.get('lead_time_days',r.get('lead_time'))].append(float(r['total_fare']))
        return [LeadTimePoint(lead_time=f"T+{d}",days=d,avg_fare=round(mean(by[d]),2) if by[d] else None,observations=len(by[d])) for d in (1,7,15,30,45)]
    def heatmap(self):
        by=defaultdict(lambda:defaultdict(list))
        for r in self.records:
            if r.get('total_fare'):by[r.get('route_id') or f"{r.get('origin')}-{r.get('destination')}"][str(r.get('observation_timestamp') or r.get('collected_at'))[:10]].append(float(r['total_fare']))
        weight={r.route_id:r.dgca_traffic_weight for r in self.routes};out=[]
        for route,days in by.items():
            ds=sorted(days)
            if not ds:continue
            latest=mean(days[ds[-1]]);prev=mean(days[ds[-2]]) if len(ds)>1 else latest;chg=(latest-prev)/prev*100 if prev else 0
            intensity='HIGH_INCREASE' if chg>=5 else 'MODERATE_INCREASE' if chg>1 else 'DECREASE' if chg<-1 else 'STABLE'
            o,d=route.split('-');out.append(HeatmapItem(route_id=route,origin=o,destination=d,current_avg_fare=round(latest,2),prev_avg_fare=round(prev,2),change_pct=round(chg,2),traffic_weight=round(weight.get(route,0),6),intensity=intensity))
        return out
