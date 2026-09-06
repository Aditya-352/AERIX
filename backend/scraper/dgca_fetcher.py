from __future__ import annotations
import csv
class BenchmarkFetchError(RuntimeError):pass

def fetch_benchmark_series(start_date:str,end_date:str,benchmark_csv:str|None=None):
    if not benchmark_csv: raise BenchmarkFetchError('Configure a DGCA TMU benchmark CSV exported from the official DGCA dataset. Expected columns: date,route_id,avg_fare.')
    out={}
    with open(benchmark_csv,encoding='utf-8',newline='') as f:
        rd=csv.DictReader(f); req={'date','route_id','avg_fare'}
        if not req.issubset(rd.fieldnames or []):raise BenchmarkFetchError(f'Missing columns: {sorted(req-set(rd.fieldnames or []))}')
        for r in rd: out[(r['date'],r['route_id'])]=float(r['avg_fare'])
    return out
