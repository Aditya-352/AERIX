from __future__ import annotations
from dataclasses import dataclass
from datetime import date
import csv, math

from scraper.dgca_fetcher import BenchmarkFetchError

def load_dgca_benchmark_csv(path: str)->dict[str,float]:
    out={}
    with open(path,encoding='utf-8',newline='') as f:
        rd=csv.DictReader(f)
        required={"date","route_id","avg_fare"}
        if not required.issubset(set(rd.fieldnames or [])): raise BenchmarkFetchError(f"DGCA benchmark CSV must contain {sorted(required)}")
        for r in rd:
            out[(r['date'],r['route_id'])]=float(r['avg_fare'])
    return out

def monthly_expand(index_series):
    return {x['period'][:7]:x['index_value'] for x in index_series}

def run_backtest(index_series:list[dict], benchmark_csv: str, route_id: str|None=None):
    if not index_series: raise BenchmarkFetchError('APIx series empty')
    bench=load_dgca_benchmark_csv(benchmark_csv)
    if route_id: bench={k:v for k,v in bench.items() if k[1]==route_id}
    # For a benchmark reported on monthly cadence, compare monthly mean APIx to monthly benchmark.
    apix={}
    for row in index_series:
        row = row.model_dump() if hasattr(row,'model_dump') else row
        apix.setdefault(row['period'][:7],[]).append(float(row['index_value']))
    pairs=[]
    for month, vals in apix.items():
        bvals=[v for (d,r),v in bench.items() if d[:7]==month]
        if bvals:pairs.append((month,sum(vals)/len(vals),sum(bvals)/len(bvals)))
    if len(pairs)<2: raise BenchmarkFetchError('Need at least two overlapping months in the supplied DGCA benchmark')
    a=[x[1] for x in pairs];b=[x[2] for x in pairs]
    mae=sum(abs(x-y) for x,y in zip(a,b))/len(a);rmse=math.sqrt(sum((x-y)**2 for x,y in zip(a,b))/len(a))
    am=sum(a)/len(a);bm=sum(b)/len(b); num=sum((x-am)*(y-bm) for x,y in zip(a,b)); den=(sum((x-am)**2 for x in a)*sum((y-bm)**2 for y in b))**0.5
    corr=num/den if den else 0
    return {"months_compared":len(pairs),"mae":round(mae,3),"rmse":round(rmse,3),"pearson_correlation":round(corr,4),"data_points":[{"month":m,"apix":round(x,3),"benchmark":round(y,3),"diff":round(x-y,3)} for m,x,y in pairs]}

class IndexBacktester:
    @staticmethod
    def run_backtest(index_series, annexure_xlsx_url=None, benchmark_csv=None):
        if not index_series: raise ValueError('Cannot backtest an empty index series')
        path=benchmark_csv
        if path is None:
            raise BenchmarkFetchError('No DGCA benchmark configured. Supply benchmark_csv with columns date,route_id,avg_fare. This fail-closed behavior prevents fabricated benchmark results.')
        return run_backtest(index_series,path)
