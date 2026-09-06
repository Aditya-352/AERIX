import pytest
from fastapi.testclient import TestClient
from main import app
from synthetic_engine import dataset_engine
from data_cleaning import DataCleaningPipeline
from index_engine import AirfareIndexEngine
from backtester import IndexBacktester
from scraper.dgca_fetcher import BenchmarkFetchError

client=TestClient(app)

def test_health_endpoint():
    r=client.get('/api/v1/health'); assert r.status_code==200; d=r.json(); assert d['status']=='HEALTHY'; assert d['demo_observations']>0

def test_search_flights_endpoint():
    d=client.get('/api/v1/search?origin=DEL&destination=BOM&departure_date=2026-09-15').json(); assert d['flights']; assert d['data_mode'] in ('LIVE','SYNTHETIC_DEMO'); assert d['flights'][0]['offers'][0]['breakdown']['total_fare']>0

def test_outlier_detection_iqr():
    o=DataCleaningPipeline.detect_outliers_iqr([5000,5100,5200,5050,4950,5150,25000]); assert o[-1] and not o[0]

def test_index_calculation():
    series=AirfareIndexEngine(dataset_engine.cleaned_observations).calculate_index_series(); assert series; assert series[0].base_index==100

def test_backtester_fails_closed_without_benchmark():
    series=AirfareIndexEngine(dataset_engine.cleaned_observations).calculate_index_series()
    with pytest.raises(BenchmarkFetchError): IndexBacktester.run_backtest(series)

def test_backtester_empty_series_raises():
    with pytest.raises(ValueError): IndexBacktester.run_backtest([])

def test_government_endpoints():
    assert client.get('/api/v1/index/overview').status_code==200
    assert len(client.get('/api/v1/routes').json())==10
    assert len(client.get('/api/v1/lead-time').json())==5
    q=client.get('/api/v1/data-quality').json(); assert 0<=q['overall_score']<=100

def test_collection_registry():
    d=client.get('/api/v1/collection/sources').json(); ids={x['source_id'] for x in d}; assert 'INDIGO_PUBLIC_ROUTE' in ids; assert 'YATRA_PUBLIC' in ids
