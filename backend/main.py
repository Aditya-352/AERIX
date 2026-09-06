from __future__ import annotations
import os, random, tempfile
from datetime import date, datetime, timedelta
from statistics import mean, median
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from models import SearchResponse, FlightCard, ProviderOffer, FareBreakdown, MethodologyConfig, DataQualityMetrics
from synthetic_engine import dataset_engine, AIRLINES, PROVIDERS
from collectors.service import CollectionService, REGISTRY
from storage.observations import ObservationStore
from data_cleaning import DataCleaningPipeline
from index_engine import AirfareIndexEngine
from analytics.features import route_trends, source_comparison, lead_time_curve, anomaly_feed, simple_forecast
from scraper.dgca_fetcher import BenchmarkFetchError
from config.settings import settings

app=FastAPI(title='AEROVA — India Airfare Price Intelligence Platform API',version='2.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
store=ObservationStore(settings.db_path)
collection=CollectionService(store)

TOTAL_SIH_SOURCES = 11
TOTAL_AIRLINES = 5
TOTAL_OTAS = 6

def live_records():
    return [r for r in store.recent(20000) if r.get('collection_status')=='SUCCESS' and r.get('total_fare') and float(r.get('total_fare') or 0)>0]

def audit_records():
    return store.recent(20000)

def demo_records():
    return dataset_engine.cleaned_observations

def api_records():
    rec = live_records()
    return rec if rec else demo_records()

def source_counts():
    st = store.stats()
    records = []
    for sid, c in REGISTRY.items():
        x = store.source_stats(sid)
        records.append({
            "source_id": sid,
            "source_name": c.source_name,
            "source_type": c.source_type,
            "source_granularity": c.source_granularity,
            "parser_version": c.parser_version,
            "status": getattr(c, 'status', 'LIVE_PUBLIC_ADAPTER'),
            "robots_status": getattr(c, 'robots_status', 'NOT_VERIFIED'),
            "authorization_status": getattr(c, 'authorization_status', 'PENDING_REVIEW'),
            "policy": getattr(c, 'policy', 'robots.txt + ToS/authorization; no CAPTCHA bypass'),
            "total_attempts": x.get('total') or 0,
            "live_observations": x.get('live') or 0,
            "success_count": x.get('success') or 0,
            "failure_count": x.get('failed') or 0,
            "last_attempt": x.get('last_attempt'),
            "last_success": x.get('last_success'),
        })
    return records

@app.get('/api/v1/health')
def health():
    live = len(live_records())
    total_store = len(audit_records())
    return {
        'status': 'HEALTHY',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'mode': 'LIVE' if live else 'SYNTHETIC_DEMO',
        'live_observations': live,
        'stored_audit_records': total_store,
        'demo_observations': len(demo_records()),
        'methodology_version': settings.methodology_version
    }

@app.get('/api/v1/collection/sources')
def collection_sources():
    return source_counts()

@app.post('/api/v1/collection/collect')
async def collect(source_id:str,origin:str,destination:str,travel_date:str,adults:int=1,cabin:str='Economy',lead_time_days:int|None=None):
    try:
        res = await collection.collect_one(source_id,origin,destination,travel_date,adults,cabin,lead_time_days)
        obs = res["observations"]
        statuses = [o.collection_status for o in obs]
        cstatus = 'SUCCESS' if any(x=='SUCCESS' and o.total_fare for x,o in zip(statuses,obs)) else ('BLOCKED' if any(o.compliance_status=='BLOCKED' for o in obs) else ('NO_DATA' if not obs or all(o.availability_status=='UNKNOWN' for o in obs) else 'FAILED'))
        return {
            'collection_status': cstatus,
            'observation_count': sum(1 for o in obs if o.collection_status=='SUCCESS' and o.total_fare),
            'reason': None if cstatus=='SUCCESS' else (obs[0].error if obs else 'No observation returned'),
            'source_id': source_id,
            'collected_at': datetime.utcnow().isoformat()+'Z',
            'inserted': res['inserted'],
            'observations': [o.model_dump() for o in obs]
        }
    except Exception as exc:
        raise HTTPException(400, str(exc))

@app.post('/api/v1/collection/collect-all')
async def collect_all(origin:str,destination:str,travel_date:str,adults:int=1,cabin:str='Economy',lead_time_days:int|None=None):
    results = []
    for sid in REGISTRY:
        results.append(await collect(sid,origin,destination,travel_date,adults,cabin,lead_time_days))
    return {'sources_attempted':len(results),'results':results,'collected_at':datetime.utcnow().isoformat()+'Z'}

@app.get('/api/v1/collection/recent')
def recent(limit:int=100):
    return audit_records()[:limit]

@app.get('/api/v1/search',response_model=SearchResponse)
def search(origin:str,destination:str,departure_date:str='2026-09-20',adults:int=1,cabin:str='Economy'):
    origin,destination=origin.upper(),destination.upper()
    records=[r for r in live_records() if r.get('origin')==origin and r.get('destination')==destination and r.get('travel_date')==departure_date]
    if records:
        grouped={}
        code={'IndiGo':'6E','Air India':'AI','Air India Express':'IX','Akasa Air':'QP','SpiceJet':'SG'}
        for r in records:
            fid=r.get('flight_number') or f"{r.get('airline','')}-{r.get('source_id')}"
            grouped.setdefault(fid,[]).append(r)
        flights=[]
        for fid,rows in grouped.items():
            offers=[]
            for r in rows:
                total=float(r['total_fare']); base=float(r.get('base_fare') or total)
                airport=float(r.get('airport_fee') or 0); convenience=float(r.get('convenience_fee') or 0); other=float(r.get('other_fee') or 0)
                taxes=float(r.get('taxes') or 0)
                mins=0
                try:
                    mins=max(0, int((datetime.utcnow() - datetime.fromisoformat(r['collected_at'].replace('Z',''))).total_seconds() / 60))
                except Exception:
                    mins=0
                offers.append(ProviderOffer(
                    provider_id=r['source_id'],provider_name=r['source_name'],is_direct=r['source_type']=='AIRLINE_DIRECT',
                    base_fare=base,taxes=taxes,fees=airport+convenience+other,total_fare=total,
                    last_checked_minutes_ago=mins,is_cheapest=False,is_best_value=False,
                    breakdown=FareBreakdown(base_fare=base,taxes=taxes,airport_fee=airport,convenience_fee=convenience,other_fee=other,total_fare=total),
                    source_status='LIVE_VERIFIED'
                ))
            c=min(o.total_fare for o in offers)
            flights.append(FlightCard(
                flight_id=fid,airline_code=code.get(rows[0].get('airline'),'XX'),airline_name=rows[0].get('airline') or rows[0]['source_name'],
                flight_number=fid,origin=origin,destination=destination,departure_time='—',arrival_time='—',duration='—',stops=0,
                cheapest_fare=c,offers=[o.model_copy(update={'is_cheapest':o.total_fare==c}) for o in offers],
                data_confidence='LIVE_PUBLIC'
            ))
        return SearchResponse(origin=origin,destination=destination,travel_date=departure_date,total_flights=len(flights),flights=flights,data_mode='LIVE',last_updated=datetime.utcnow().isoformat()+'Z')

    random.seed(f'{origin}-{destination}-{departure_date}')
    airlines=AIRLINES; times=[('06:00','08:15'),('08:30','10:45'),('11:15','13:30'),('14:00','16:15'),('17:30','19:45'),('20:00','22:15')]
    flights=[]
    for i,(dep,arr) in enumerate(times):
        a=airlines[i%len(airlines)]; raw=5600*a['price_mult']*random.uniform(.96,1.04); offers=[]
        for p in PROVIDERS:
            bf=raw*(1+p['variance']); tx=bf*.16; af=200; cf=p['fee']; total=round(bf+tx+af+cf,2)
            offers.append(ProviderOffer(
                provider_id=p['id'],provider_name=p['name'],is_direct=p['id']=='DIRECT',
                base_fare=round(bf,2),taxes=round(tx,2),fees=af+cf,total_fare=total,
                last_checked_minutes_ago=None,is_cheapest=False,is_best_value=False,
                breakdown=FareBreakdown(base_fare=round(bf,2),taxes=round(tx,2),airport_fee=af,convenience_fee=cf,total_fare=total),
                source_status='DEMO'
            ))
        c=min(o.total_fare for o in offers)
        offers=[o.model_copy(update={'is_cheapest':o.total_fare==c}) for o in offers]
        flights.append(FlightCard(
            flight_id=f"{a['code']}-{i}-{departure_date}",airline_code=a['code'],airline_name=a['name'],
            flight_number=f"{a['code']} {100+i*123}",origin=origin,destination=destination,
            departure_time=dep,arrival_time=arr,duration='2h 15m',stops=0,
            cheapest_fare=c,offers=offers,data_confidence='DEMO'
        ))
    return SearchResponse(origin=origin,destination=destination,travel_date=departure_date,total_flights=len(flights),flights=flights,data_mode='SYNTHETIC_DEMO',last_updated=datetime.utcnow().isoformat()+'Z')

_demo_cache = {}

def get_demo_artifacts():
    if not _demo_cache:
        demo = demo_records()
        clean = DataCleaningPipeline.clean(demo)
        engine = AirfareIndexEngine(clean, base_period=settings.base_period)
        series = engine.calculate_index_series()
        quality = DataCleaningPipeline.compute_quality_metrics(demo)
        _demo_cache.update({
            'clean': clean,
            'engine': engine,
            'series': series,
            'quality': quality,
            'basket': engine.route_basket(),
            'heatmap': engine.heatmap(),
            'lead_time': engine.lead_time_curve(),
            'source_comp': source_comparison(demo),
            'anomalies': anomaly_feed(demo)[:30],
            'forecast': simple_forecast(demo, 7),
        })
    return _demo_cache

@app.get('/api/v1/government/overview')
def government_overview():
    live = live_records()
    sources = source_counts()
    if live:
        clean = DataCleaningPipeline.clean(live)
        engine = AirfareIndexEngine(clean, base_period=settings.base_period)
        series = engine.calculate_index_series()
        latest = series[-1] if series else None
        q = DataCleaningPipeline.compute_quality_metrics(live)
        return {
            'index_latest': latest.model_dump() if latest else None,
            'index_series': [x.model_dump() for x in series[-90:]],
            'route_basket': [x.model_dump() for x in engine.route_basket()],
            'heatmap': [x.model_dump() for x in engine.heatmap()],
            'lead_time': [x.model_dump() for x in engine.lead_time_curve()],
            'quality': q,
            'source_comparison': source_comparison(live),
            'anomalies': anomaly_feed(live)[:30],
            'forecast': simple_forecast(live, 7),
            'data_mode': 'LIVE',
            'live_verified_observations': len(live),
            'total_synthetic_observations': len(demo_records()),
            'current_indexed_observations': latest.total_observations if latest else 0,
            'live_routes_count': store.live_routes(),
            'synthetic_routes_count': 20,
            'enabled_sources_count': sum(1 for x in sources if x['status']=='LIVE_PUBLIC_ADAPTER'),
            'total_sources_count': TOTAL_SIH_SOURCES,
            'enabled_airlines_count': sum(1 for x in sources if x['source_type']=='AIRLINE_DIRECT' and x['status']=='LIVE_PUBLIC_ADAPTER'),
            'enabled_ota_count': sum(1 for x in sources if x['source_type']=='OTA' and x['status']=='LIVE_PUBLIC_ADAPTER'),
            'official_benchmark_availability': False,
            'benchmark_status': 'NOT RUN — VERIFIED BENCHMARK REQUIRED',
            'last_updated': datetime.utcnow().isoformat() + 'Z'
        }
    d = get_demo_artifacts()
    series = d['series']
    latest = series[-1] if series else None
    return {
        'index_latest': latest.model_dump() if latest else None,
        'index_series': [x.model_dump() for x in series[-90:]],
        'route_basket': [x.model_dump() for x in d['basket']],
        'heatmap': [x.model_dump() for x in d['heatmap']],
        'lead_time': [x.model_dump() for x in d['lead_time']],
        'quality': d['quality'],
        'source_comparison': d['source_comp'],
        'anomalies': d['anomalies'],
        'forecast': d['forecast'],
        'data_mode': 'SYNTHETIC_DEMO',
        'live_verified_observations': len(live),
        'total_synthetic_observations': len(demo_records()),
        'current_indexed_observations': latest.total_observations if latest else 0,
        'live_routes_count': store.live_routes(),
        'synthetic_routes_count': 20,
        'enabled_sources_count': sum(1 for x in sources if x['status']=='LIVE_PUBLIC_ADAPTER'),
        'total_sources_count': TOTAL_SIH_SOURCES,
        'enabled_airlines_count': sum(1 for x in sources if x['source_type']=='AIRLINE_DIRECT' and x['status']=='LIVE_PUBLIC_ADAPTER'),
        'enabled_ota_count': sum(1 for x in sources if x['source_type']=='OTA' and x['status']=='LIVE_PUBLIC_ADAPTER'),
        'official_benchmark_availability': False,
        'benchmark_status': 'NOT RUN — VERIFIED BENCHMARK REQUIRED',
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }

@app.get('/api/v1/government/backtest/status')
def backtest_status():
    return {
        'status': 'NOT_READY',
        'benchmark_name': 'DGCA Tariff Monitoring Unit (TMU) Export',
        'benchmark_observations': 0,
        'api_observations': len(api_records()),
        'official_benchmark_available': False,
        'message': 'NOT RUN — VERIFIED BENCHMARK REQUIRED',
        'policy': 'Synthetic benchmark comparisons are prohibited.'
    }

@app.get('/api/v1/index/overview')
def index_overview():
    live = live_records()
    if live:
        clean = DataCleaningPipeline.clean(live)
        series = AirfareIndexEngine(clean, base_period=settings.base_period).calculate_index_series()
        latest = series[-1] if series else None
        return {"current_apix":latest.index_value if latest else None,"daily_change":latest.daily_change_pct if latest else 0,"weekly_change":latest.weekly_change_pct if latest else 0,"monthly_change":latest.monthly_change_pct if latest else 0,"series":[x.model_dump() for x in series],"data_mode":"LIVE"}
    d = get_demo_artifacts()
    series = d['series']
    latest = series[-1] if series else None
    return {"current_apix":latest.index_value if latest else None,"daily_change":latest.daily_change_pct if latest else 0,"weekly_change":latest.weekly_change_pct if latest else 0,"monthly_change":latest.monthly_change_pct if latest else 0,"series":[x.model_dump() for x in series],"data_mode":"SYNTHETIC_DEMO"}

@app.get('/api/v1/routes')
def routes_endpoint():
    live = live_records()
    if live:
        return [x.model_dump() for x in AirfareIndexEngine(DataCleaningPipeline.clean(live), base_period=settings.base_period).route_basket()[:10]]
    d = get_demo_artifacts()
    return [x.model_dump() for x in d['basket'][:10]]

@app.get('/api/v1/lead-time')
def lead_time_endpoint():
    live = live_records()
    if live:
        return [x.model_dump() for x in AirfareIndexEngine(DataCleaningPipeline.clean(live), base_period=settings.base_period).lead_time_curve()]
    d = get_demo_artifacts()
    return [x.model_dump() for x in d['lead_time']]

@app.get('/api/v1/data-quality',response_model=DataQualityMetrics)
def quality_endpoint():
    live = live_records()
    if live:
        return DataCleaningPipeline.compute_quality_metrics(live)
    d = get_demo_artifacts()
    return d['quality']

@app.get('/api/v1/government/trends')
def trends(): return route_trends(api_records())

@app.get('/api/v1/government/methodology',response_model=MethodologyConfig)
def methodology(): return MethodologyConfig(base_period=settings.base_period)

@app.post('/api/v1/government/backtest',response_model=dict)
async def backtest(benchmark_csv: str|None = Query(default=None), file: UploadFile|None = File(default=None)):
    live = live_records()
    if live:
        clean = DataCleaningPipeline.clean(live)
        series = AirfareIndexEngine(clean, base_period=settings.base_period).calculate_index_series()
    else:
        d = get_demo_artifacts()
        series = d['series']
    path = benchmark_csv
    tmp = None
    try:
        if file is not None:
            data = await file.read()
            fd, tmp = tempfile.mkstemp(suffix='.csv')
            os.close(fd)
            with open(tmp, 'wb') as f:
                f.write(data)
            path = tmp
        if not path:
            return {'status': 'NOT_READY', 'message': 'NOT RUN — VERIFIED BENCHMARK REQUIRED', 'result': None}
        from backtester import run_backtest
        return {'status': 'OK', 'result': run_backtest(series, path)}
    except (BenchmarkFetchError, ValueError, Exception) as exc:
        return {'status': 'NOT_READY', 'message': str(exc), 'result': None}
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
