from __future__ import annotations
import math, statistics
from collections import Counter

def iqr_flags(values: list[float], factor: float=1.5):
    if len(values)<4:return [False]*len(values)
    xs=sorted(values); q1=xs[(len(xs)-1)//4];q3=xs[3*(len(xs)-1)//4];iqr=q3-q1
    if iqr==0:return [False]*len(values)
    lo,hi=q1-factor*iqr,q3+factor*iqr
    return [x<lo or x>hi for x in values]

def robust_mad_flags(values:list[float],threshold:float=3.5):
    if len(values)<4:return [False]*len(values)
    med=statistics.median(values);dev=[abs(x-med) for x in values];mad=statistics.median(dev)
    if mad==0:return [False]*len(values)
    return [0.6745*abs(x-med)/mad>threshold for x in values]

def quality_summary(records:list[dict], attempted:int|None=None):
    n=len(records)
    if not n:return {"overall_score":0.0,"completeness":0.0,"duplicate_rate":0.0,"missing_fare_rate":0.0,"outlier_rate":0.0,"collection_success_rate":0.0 if attempted else None,"last_updated":None}
    fares=[float(r.get('total_fare') or 0) for r in records]
    missing=sum(x<=0 for x in fares)
    flags_i=iqr_flags([x for x in fares if x>0]); flags_m=robust_mad_flags([x for x in fares if x>0])
    out=sum(a or b for a,b in zip(flags_i,flags_m)) if flags_i else 0
    keys=[(r.get('source_id'),r.get('origin'),r.get('destination'),r.get('travel_date'),r.get('flight_number'),r.get('collected_at')) for r in records]
    dup=n-len(set(keys))
    completeness=100*(1-missing/n)
    duplicate_rate=100*dup/n
    outlier_rate=100*out/n
    success=100*(n/attempted) if attempted else None
    score=max(0,min(100,100-3*missing/n*100-0.5*duplicate_rate-1.2*outlier_rate))
    return {"overall_score":round(score,2),"completeness":round(completeness,2),"duplicate_rate":round(duplicate_rate,2),"missing_fare_rate":round(100*missing/n,2),"outlier_rate":round(outlier_rate,2),"collection_success_rate":round(success,2) if success is not None else None,"last_updated":records[0].get('collected_at')}
