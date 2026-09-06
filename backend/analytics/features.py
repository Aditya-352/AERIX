from __future__ import annotations
from collections import defaultdict
from statistics import mean, median

def clean_records(records:list[dict])->list[dict]:
    valid=[]
    for r in records:
        if str(r.get('collection_status'))!='SUCCESS': continue
        if r.get('availability_status') not in ("AVAILABLE","UNKNOWN"): continue
        fare=r.get('total_fare')
        if fare is None or float(fare)<=0: continue
        x=dict(r); x['total_fare']=float(fare); valid.append(x)
    by_route=defaultdict(list)
    for r in valid: by_route[(r['origin'],r['destination'])].append(r['total_fare'])
    out=[]
    for r in valid:
        vals=by_route[(r['origin'],r['destination'])]
        med=median(vals); r['robust_deviation_pct']=round(abs(r['total_fare']-med)/med*100,2) if med else 0
        if r['robust_deviation_pct']<=60: out.append(r)
    return out

def route_trends(records:list[dict]):
    by=defaultdict(lambda: defaultdict(list))
    for r in records: by[(r['origin'],r['destination'])][r['travel_date']].append(r['total_fare'])
    result=[]
    for route, days in by.items():
        ordered=sorted(days)
        latest=mean(days[ordered[-1]])
        prev=mean(days[ordered[-2]]) if len(ordered)>1 else latest
        result.append({"route_id":f"{route[0]}-{route[1]}","origin":route[0],"destination":route[1],"current_avg_fare":round(latest,2),"prev_avg_fare":round(prev,2),"change_pct":round((latest-prev)/prev*100,2) if prev else 0})
    return sorted(result,key=lambda x:abs(x['change_pct']),reverse=True)

def source_comparison(records:list[dict]):
    by=defaultdict(list)
    for r in records:by[r['source_id']].append(r['total_fare'])
    return [{"source_id":k,"avg_fare":round(mean(v),2),"median_fare":round(median(v),2),"min_fare":round(min(v),2),"max_fare":round(max(v),2),"observations":len(v)} for k,v in sorted(by.items())]

def lead_time_curve(records:list[dict]):
    by=defaultdict(list)
    for r in records:
        lt=r.get('lead_time_days')
        if lt in (1,7,15,30,45): by[lt].append(r['total_fare'])
    return [{"lead_time":f"T+{d}","days":d,"avg_fare":round(mean(by[d]),2) if by[d] else None,"observations":len(by[d])} for d in (1,7,15,30,45)]

def anomaly_feed(records:list[dict], z_threshold:float=3.5):
    cleaned=clean_records(records); by=defaultdict(list)
    for r in cleaned:by[(r['origin'],r['destination'],r['travel_date'])].append(r['total_fare'])
    events=[]
    for key,vals in by.items():
        if len(vals)<4:continue
        med=median(vals); mad=median([abs(x-med) for x in vals])
        if mad==0:continue
        for r in [x for x in cleaned if (x['origin'],x['destination'],x['travel_date'])==key]:
            mz=0.6745*abs(r['total_fare']-med)/mad
            if mz>z_threshold: events.append({"route_id":f"{key[0]}-{key[1]}","travel_date":key[2],"fare":r['total_fare'],"modified_z":round(mz,2),"source_id":r['source_id']})
    return events

def simple_forecast(records:list[dict],days:int=7):
    cleaned=clean_records(records); by=defaultdict(list)
    for r in cleaned:by[r['travel_date']].append(r['total_fare'])
    hist=[(d,mean(v)) for d,v in sorted(by.items())]
    if len(hist)<2:return []
    vals=[v for _,v in hist[-7:]]; drift=(vals[-1]-vals[0])/max(1,len(vals)-1)
    last=vals[-1]
    from datetime import date,timedelta
    end=date.fromisoformat(hist[-1][0])
    return [{"date":(end+timedelta(days=i)).isoformat(),"forecast":round(last+drift*i,2),"method":"7-point linear drift"} for i in range(1,days+1)]
