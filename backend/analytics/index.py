from __future__ import annotations
from collections import defaultdict
from statistics import mean
from config.settings import settings
from routes.registry import normalized_routes

class IndexEngine:
    def __init__(self, records:list[dict], routes=None): self.records=records; self.routes=normalized_routes(routes or []) if routes else normalized_routes()
    def _eligible(self): return [r for r in self.records if r.get('collection_status')=='SUCCESS' and r.get('source_granularity') in ('FLIGHT_LEVEL','DATE_LEVEL_ROUTE_SIGNAL') and r.get('availability_status') in ('AVAILABLE','UNKNOWN') and r.get('total_fare') and float(r['total_fare'])>0]
    def series(self):
        rec=self._eligible(); by=defaultdict(lambda:defaultdict(list))
        for r in rec:by[r['collected_at'][:10]][r['origin']+'-'+r['destination']].append(float(r['total_fare']))
        dates=sorted(by)
        if not dates:return []
        # fixed base period for methodology; if no observations exist there, the first observed period is used
        base_date=next((d for d in dates if d.startswith(settings.base_period)),dates[0])
        route_base={rid:mean(v) for rid,v in by[base_date].items()} if base_date in by else {rid:mean(sum([list(x.values()) for x in by[d].values()],[])) for rid in by for x in []}
        if not route_base:
            route_base={rid:mean(by[d][rid]) for d in dates for rid in by[d] if rid not in route_base} if dates else {}
        weight={r.route_id:r.dgca_traffic_weight for r in self.routes}
        def agg(day):
            vals=[]
            for rid,w in weight.items():
                if rid in by[day]: vals.append((w,mean(by[day][rid])))
            if not vals:return None
            totalw=sum(w for w,_ in vals);return sum(w*v for w,v in vals)/totalw
        base=agg(base_date) or agg(dates[0])
        result=[]
        prev=None
        for d in dates:
            cur=agg(d)
            if cur is None:continue
            idx=cur/base*100
            week=next((x['index_value'] for x in reversed(result) if (date_delta(d,x['period'])>=7)),result[0]['index_value'] if result else 100)
            month=result[0]['index_value'] if result else 100
            result.append({"period":d,"index_value":round(idx,2),"base_period":base_date,"base_index":100,"daily_change_pct":round((idx-prev)/prev*100,2) if prev else 0,"weekly_change_pct":round((idx-week)/week*100,2) if week else 0,"monthly_change_pct":round((idx-month)/month*100,2) if month else 0,"total_routes":len(weight),"total_observations":sum(len(v) for v in by[d].values()),"methodology_version":settings.methodology_version})
            prev=idx
        return result

def date_delta(a,b):
    from datetime import date
    return (date.fromisoformat(a)-date.fromisoformat(b)).days
