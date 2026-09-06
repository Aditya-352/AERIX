from __future__ import annotations
import os, random
from datetime import date, datetime, timedelta
from statistics import mean, median
from fastapi import FastAPI, Query, HTTPException
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

def live_records(): return store.recent(20000)
def demo_records(): return dataset_engine.cleaned_observations

def api_records():
    rec=live_records()
    return rec if rec else demo_records()

@app.get('/api/v1/health')
def health():
    live=len(live_records())
    return {'status':'HEALTHY','timestamp':datetime.utcnow().isoformat()+'Z','mode':'LIVE' if live else 'SYNTHETIC_DEMO','live_observations':live,'demo_observations':len(demo_records()),'methodology_version':settings.methodology_version}

@app.get('/api/v1/collection/sources')
def collection_sources():
    return [{'source_id':sid,'source_name':c.source_name,'source_type':c.source_type,'source_granularity':c.source_granularity,'parser_version':c.parser_version,'policy':'robots.txt + ToS/authorization; no CAPTCHA bypass'} for sid,c in REGISTRY.items()]

@app.post('/api/v1/collection/collect')
async def collect(source_id:str,origin:str,destination:str,travel_date:str,adults:int=1,cabin:str='Economy',lead_time_days:int|None=None):
    try:return await collection.collect_one(source_id,origin,destination,travel_date,adults,cabin,lead_time_days)
    except Exception as exc:raise HTTPException(400,str(exc))

@app.post('/api/v1/collection/collect-all')
async def collect_all(origin:str,destination:str,travel_date:str,adults:int=1,cabin:str='Economy',lead_time_days:int|None=None):
    results=[]
    for sid in REGISTRY:
        results.append(await collection.collect_one(sid,origin,destination,travel_date,adults,cabin,lead_time_days))
    return {'sources_attempted':len(results),'results':results,'collected_at':datetime.utcnow().isoformat()+'Z'}

@app.get('/api/v1/collection/recent')
def recent(limit:int=100):return store.recent(limit)

@app.get('/api/v1/search',response_model=SearchResponse)
def search(origin:str,destination:str,departure_date:str='2026-09-20',adults:int=1,cabin:str='Economy'):
    origin,destination=origin.upper(),destination.upper()
    records=[r for r in live_records() if r.get('origin')==origin and r.get('destination')==destination and r.get('travel_date')==departure_date and r.get('total_fare')]
    if records:
        grouped={}
        for r in records:
            fid=r.get('flight_number') or f"{r.get('airline','')}-{r.get('source_id')}"
            grouped.setdefault(fid,[]).append(r)
        flights=[]
        code={'IndiGo':'6E','Air India':'AI','Air India Express':'IX','Akasa Air':'QP','SpiceJet':'SG'}
        for fid,rows in grouped.items():
            offers=[]
            for r in rows:
                total=float(r['total_fare']);base=float(r.get('base_fare') or total)
                offers.append(ProviderOffer(provider_id=r['source_id'],provider_name=r['source_name'],is_direct=r['source_type']=='AIRLINE_DIRECT',base_fare=base,taxes=float(r.get('taxes') or 0),fees=float(r.get('convenience_fee') or 0)+float(r.get('airport_fee') or 0)+float(r.get('other_fee') or 0),total_fare=total,last_checked_minutes_ago=0,is_cheapest=False,is_best_value=False,breakdown=FareBreakdown(base_fare=base,taxes=float(r.get('taxes') or 0),airport_fee=float(r.get('airport_fee') or 0),convenience_fee=float(r.get('convenience_fee') or 0),other_fee=float(r.get('other_fee') or 0),total_fare=total),source_status='LIVE'))
            c=min(o.total_fare for o in offers); flights.append(FlightCard(flight_id=fid,airline_code=code.get(rows[0].get('airline'),'XX'),airline_name=rows[0].get('airline') or rows[0]['source_name'],flight_number=fid,origin=origin,destination=destination,departure_time='—',arrival_time='—',duration='—',stops=0,cheapest_fare=c,offers=[o.model_copy(update={'is_cheapest':o.total_fare==c}) for o in offers],data_confidence='LIVE_PUBLIC'))
        return SearchResponse(origin=origin,destination=destination,travel_date=departure_date,total_flights=len(flights),flights=flights,data_mode='LIVE',last_updated=datetime.utcnow().isoformat()+'Z')
    # fallback demo search, transparently labelled
    random.seed(f'{origin}-{destination}-{departure_date}')
    airlines=AIRLINES; times=[('06:00','08:15'),('08:30','10:45'),('11:15','13:30'),('14:00','16:15'),('17:30','19:45'),('20:00','22:15')]
    flights=[]
    for i,(dep,arr) in enumerate(times):
        a=airlines[i%len(airlines)]; raw=5600*a['price_mult']*random.uniform(.96,1.04);offers=[]
        for p in PROVIDERS:
            bf=raw*(1+p['variance']);tx=bf*.16;af=200;cf=p['fee'];total=round(bf+tx+af+cf,2)
            offers.append(ProviderOffer(provider_id=p['id'],provider_name=p['name'],is_direct=p['id']=='DIRECT',base_fare=round(bf,2),taxes=round(tx,2),fees=af+cf,total_fare=total,last_checked_minutes_ago=None,is_cheapest=False,is_best_value=False,breakdown=FareBreakdown(base_fare=round(bf,2),taxes=round(tx,2),airport_fee=af,convenience_fee=cf,total_fare=total),source_status='DEMO'))
        c=min(o.total_fare for o in offers);offers=[o.model_copy(update={'is_cheapest':o.total_fare==c}) for o in offers]
        flights.append(FlightCard(flight_id=f"{a['code']}-{i}-{departure_date}",airline_code=a['code'],airline_name=a['name'],flight_number=f"{a['code']} {100+i*123}",origin=origin,destination=destination,departure_time=dep,arrival_time=arr,duration='2h 15m',stops=0,cheapest_fare=c,offers=offers,data_confidence='DEMO'))
    return SearchResponse(origin=origin,destination=destination,travel_date=departure_date,total_flights=len(flights),flights=flights,data_mode='SYNTHETIC_DEMO',last_updated=datetime.utcnow().isoformat()+'Z')

@app.get('/api/v1/government/overview')
def government_overview():
    raw=api_records(); clean=DataCleaningPipeline.clean(raw);engine=AirfareIndexEngine(clean,base_period=settings.base_period);series=engine.calculate_index_series(); latest=series[-1] if series else None
    q=DataCleaningPipeline.compute_quality_metrics(raw)
    return {'index_latest':latest.model_dump() if latest else None,'index_series':[x.model_dump() for x in series[-90:]],'route_basket':[x.model_dump() for x in engine.route_basket()],'heatmap':[x.model_dump() for x in engine.heatmap()], 'lead_time':[x.model_dump() for x in engine.lead_time_curve()], 'quality':q,'source_comparison':source_comparison(raw),'anomalies':anomaly_feed(raw)[:30],'forecast':simple_forecast(raw,7),'data_mode':'LIVE' if live_records() else 'SYNTHETIC_DEMO','last_updated':datetime.utcnow().isoformat()+'Z'}

@app.get('/api/v1/index/overview')
def index_overview():
    raw=api_records(); clean=DataCleaningPipeline.clean(raw); series=AirfareIndexEngine(clean,base_period=settings.base_period).calculate_index_series(); latest=series[-1] if series else None
    return {"current_apix":latest.index_value if latest else None,"daily_change":latest.daily_change_pct if latest else 0,"weekly_change":latest.weekly_change_pct if latest else 0,"monthly_change":latest.monthly_change_pct if latest else 0,"series":[x.model_dump() for x in series],"data_mode":"LIVE" if live_records() else "SYNTHETIC_DEMO"}

@app.get('/api/v1/routes')
def routes_endpoint():
    # Legacy endpoint retained for compatibility; government overview exposes full basket.
    return [x.model_dump() for x in AirfareIndexEngine(DataCleaningPipeline.clean(api_records()),base_period=settings.base_period).route_basket()[:10]]

@app.get('/api/v1/lead-time')
def lead_time_endpoint(): return [x.model_dump() for x in AirfareIndexEngine(DataCleaningPipeline.clean(api_records()),base_period=settings.base_period).lead_time_curve()]

@app.get('/api/v1/data-quality',response_model=DataQualityMetrics)
def quality_endpoint(): return DataCleaningPipeline.compute_quality_metrics(api_records())

@app.get('/api/v1/government/trends')
def trends():return route_trends(api_records())

@app.get('/api/v1/government/methodology',response_model=MethodologyConfig)
def methodology():return MethodologyConfig(base_period=settings.base_period)

@app.post('/api/v1/government/backtest')
def backtest(benchmark_csv:str):
    raw=api_records();clean=DataCleaningPipeline.clean(raw);series=AirfareIndexEngine(clean,base_period=settings.base_period).calculate_index_series()
    try:
        from backtester import run_backtest
        return {'status':'OK','result':run_backtest(series,benchmark_csv)}
    except BenchmarkFetchError as exc:
        return {'status':'NOT_READY','message':str(exc)}
