import pytest
from fastapi.testclient import TestClient
from main import app
from synthetic_engine import dataset_engine
from data_cleaning import DataCleaningPipeline
from index_engine import AirfareIndexEngine
from backtester import IndexBacktester
from scraper.dgca_fetcher import BenchmarkFetchError
from analytics.quality import quality_summary, observation_identity_key
from routes.registry import ROUTES, normalized_routes

client = TestClient(app)

def test_health_endpoint():
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    d = r.json()
    assert d['status'] == 'HEALTHY'
    assert d['demo_observations'] == 45000
    assert d['methodology_version'] == '2.0'

def test_search_flights_endpoint():
    d = client.get('/api/v1/search?origin=DEL&destination=BOM&departure_date=2026-09-15').json()
    assert d['flights']
    assert d['data_mode'] in ('LIVE', 'SYNTHETIC_DEMO')
    assert d['flights'][0]['offers'][0]['breakdown']['total_fare'] > 0
    assert d['flights'][0]['data_confidence'] == 'DEMO'

def test_outlier_detection_iqr():
    o = DataCleaningPipeline.detect_outliers_iqr([5000, 5100, 5200, 5050, 4950, 5150, 25000])
    assert o[-1] and not o[0]

def test_index_calculation():
    series = AirfareIndexEngine(dataset_engine.cleaned_observations).calculate_index_series()
    assert series
    assert series[0].base_index == 100

def test_backtester_fails_closed_without_benchmark():
    series = AirfareIndexEngine(dataset_engine.cleaned_observations).calculate_index_series()
    with pytest.raises(BenchmarkFetchError):
        IndexBacktester.run_backtest(series)

def test_backtester_empty_series_raises():
    with pytest.raises(ValueError):
        IndexBacktester.run_backtest([])

def test_government_endpoints():
    assert client.get('/api/v1/index/overview').status_code == 200
    ov = client.get('/api/v1/government/overview')
    assert ov.status_code == 200
    res = ov.json()
    assert 'index_latest' in res
    assert len(res['heatmap']) > 0
    assert len(client.get('/api/v1/routes').json()) == 10
    assert len(client.get('/api/v1/lead-time').json()) == 5
    q = client.get('/api/v1/data-quality').json()
    assert 0 <= q['overall_score'] <= 100
    assert q['duplicate_rate'] == 0.0

def test_collection_registry():
    d = client.get('/api/v1/collection/sources').json()
    ids = {x['source_id'] for x in d}
    assert len(d) == 11
    assert 'INDIGO_PUBLIC_ROUTE' in ids
    assert 'YATRA_PUBLIC' in ids
    assert 'EASEMYTRIP_PUBLIC' in ids
    assert 'AIR_INDIA_EXPRESS_PUBLIC_ROUTE' in ids
    assert 'AIR_INDIA_PUBLIC_ROUTE' in ids
    assert 'AKASA_PUBLIC_ROUTE' in ids
    assert 'SPICEJET_PUBLIC_ROUTE' in ids
    assert 'MMT_AUTHORIZED' in ids
    assert 'CLEARTRIP_AUTHORIZED' in ids
    assert 'IXIGO_AUTHORIZED' in ids
    assert 'GOIBIBO_AUTHORIZED' in ids

def test_duplicate_semantics_true_duplicate():
    """True duplicates have identical source, route, airline, flight, travel date, cabin, and collection timestamp."""
    rec1 = {
        "source_id": "INDIGO_PUBLIC_ROUTE", "origin": "DEL", "destination": "BOM",
        "airline": "IndiGo", "flight_number": "6E 204", "fare_class": "Economy",
        "travel_date": "2026-09-20", "collected_at": "2026-09-06T10:00:00Z", "total_fare": 5400.0
    }
    rec2 = dict(rec1)  # Exact duplicate
    q = quality_summary([rec1, rec2])
    assert q["true_duplicate_count"] == 1
    assert q["duplicate_rate"] == 50.0

def test_legitimate_repeated_observation():
    """Same flight observed at a different collection time is a legitimate repeated observation, NOT a duplicate."""
    rec1 = {
        "source_id": "INDIGO_PUBLIC_ROUTE", "origin": "DEL", "destination": "BOM",
        "airline": "IndiGo", "flight_number": "6E 204", "fare_class": "Economy",
        "travel_date": "2026-09-20", "collected_at": "2026-09-06T10:00:00Z", "total_fare": 5400.0
    }
    rec2 = dict(rec1, collected_at="2026-09-06T14:00:00Z", total_fare=5650.0)
    q = quality_summary([rec1, rec2])
    assert q["true_duplicate_count"] == 0
    assert q["duplicate_rate"] == 0.0

def test_same_flight_different_travel_dates():
    """Same flight number on different travel dates represents distinct scheduled flights, NOT duplicates."""
    rec1 = {
        "source_id": "INDIGO_PUBLIC_ROUTE", "origin": "DEL", "destination": "BOM",
        "airline": "IndiGo", "flight_number": "6E 204", "fare_class": "Economy",
        "travel_date": "2026-09-20", "collected_at": "2026-09-06T10:00:00Z", "total_fare": 5400.0
    }
    rec2 = dict(rec1, travel_date="2026-09-21", total_fare=5800.0)
    q = quality_summary([rec1, rec2])
    assert q["true_duplicate_count"] == 0
    assert q["duplicate_rate"] == 0.0

def test_route_weight_validation():
    """Verify sum of normalized route weights equals 1.0, no negative weights, valid IATA codes, and no duplicate routes."""
    routes = normalized_routes(ROUTES)
    assert len(routes) == 20
    total_weight = sum(r.dgca_traffic_weight for r in routes)
    assert pytest.approx(total_weight, 1e-6) == 1.0
    route_ids = [r.route_id for r in routes]
    assert len(route_ids) == len(set(route_ids)), "Duplicate routes detected in basket"
    for r in routes:
        assert r.dgca_traffic_weight > 0, f"Non-positive weight on {r.route_id}"
        assert len(r.origin) == 3 and r.origin.isalpha() and r.origin.isupper(), f"Invalid origin IATA {r.origin}"
        assert len(r.destination) == 3 and r.destination.isalpha() and r.destination.isupper(), f"Invalid destination IATA {r.destination}"

def test_backtest_status_endpoint():
    r = client.get('/api/v1/government/backtest/status')
    assert r.status_code == 200
    d = r.json()
    assert d['status'] == 'NOT_READY'
    assert d['official_benchmark_available'] is False
    assert 'NOT RUN' in d['message']

def test_backtest_upload_and_calculation(tmp_path):
    """Verify backtest endpoint accepts a verified benchmark CSV via file upload and runs calculation."""
    csv_content = (
        "date,route_id,avg_fare\n"
        "2026-07-01,DEL-BOM,5600.0\n"
        "2026-07-15,DEL-BLR,6200.0\n"
        "2026-08-01,DEL-BOM,5800.0\n"
        "2026-08-15,DEL-BLR,6400.0\n"
    )
    p = tmp_path / "benchmark.csv"
    p.write_text(csv_content, encoding="utf-8")
    with open(p, "rb") as f:
        r = client.post('/api/v1/government/backtest', files={'file': ('benchmark.csv', f, 'text/csv')})
    assert r.status_code == 200
    res = r.json()
    assert res['status'] == 'OK'
    assert res['result']['months_compared'] == 2
    assert 'mae' in res['result']
    assert 'rmse' in res['result']
    assert 'pearson_correlation' in res['result']

def test_backtest_without_benchmark_returns_not_ready():
    r = client.post('/api/v1/government/backtest')
    assert r.status_code == 200
    res = r.json()
    assert res['status'] == 'NOT_READY'
    assert 'NOT RUN' in res['message']
