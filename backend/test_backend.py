import pytest
from fastapi.testclient import TestClient
from main import app
from synthetic_engine import dataset_engine
from data_cleaning import DataCleaningPipeline
from index_engine import AirfareIndexEngine
from backtester import IndexBacktester
from scraper.dgca_fetcher import BenchmarkFetchError

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["dataset_observations"] > 0

def test_search_flights_endpoint():
    response = client.get("/api/v1/search?origin=DEL&destination=BOM&departure_date=2026-09-15")
    assert response.status_code == 200
    data = response.json()
    assert data["origin"] == "DEL"
    assert data["destination"] == "BOM"
    assert len(data["flights"]) > 0

    first_flight = data["flights"][0]
    assert "offers" in first_flight
    assert len(first_flight["offers"]) > 0

    # Ensure provider offers include breakdown
    offer = first_flight["offers"][0]
    assert "breakdown" in offer
    assert offer["breakdown"]["base_fare"] > 0
    assert offer["breakdown"]["taxes"] >= 0
    assert offer["breakdown"]["total_fare"] > 0

def test_outlier_detection_iqr():
    fares = [5000, 5100, 5200, 5050, 4950, 5150, 25000]  # 25000 is an outlier
    outliers = DataCleaningPipeline.detect_outliers_iqr(fares)
    assert outliers[-1] == True
    assert outliers[0] == False

def test_index_calculation():
    engine = AirfareIndexEngine(dataset_engine.cleaned_observations)
    series = engine.calculate_index_series()
    assert len(series) > 0
    first_point = series[0]
    assert first_point.base_index == 100.0
    assert first_point.index_value > 0

def test_backtester_requires_real_credentials():
    """
    PREVIOUSLY this test called run_backtest(series) with no arguments and
    asserted the returned correlation was plausible-looking. That passed
    because the old implementation fabricated a benchmark from noised APIx
    values — the test was validating that the fabrication looked
    reasonable, not that the index tracks anything real.

    The rewritten run_backtest() requires a real annexure_xlsx_url (a
    direct link to the current month's MoSPI CPI Annexure I release — see
    scraper/dgca_fetcher.py) and raises BenchmarkFetchError without one,
    rather than returning plausible-but-fake numbers. This test asserts
    that refusal.
    """
    engine = AirfareIndexEngine(dataset_engine.cleaned_observations)
    series = engine.calculate_index_series()
    with pytest.raises(BenchmarkFetchError):
        IndexBacktester.run_backtest(series)


def test_backtester_empty_series_raises():
    """PREVIOUSLY an empty series silently returned hardcoded placeholder
    numbers (apix_mean=107.5, pearson_correlation=0.978, etc.) instead of
    signaling that no backtest could be run."""
    with pytest.raises(ValueError):
        IndexBacktester.run_backtest([])


# NOTE: a real integration test — asserting actual MAE/RMSE/correlation
# values against a live MoSPI Annexure I fetch — needs a current month's
# real annexure_xlsx_url AND completion of dgca_fetcher.py's documented
# "REMAINING VERIFICATION STEP" (confirming the real Excel column layout,
# since the current offset is an untested guess — see that file's
# docstring). Add that test once both are done; do not add one against an
# unverified column offset now, since a "passing" test against a guessed
# silently reintroduce exactly the false-confidence problem this rewrite
# removes.

def test_index_overview_and_endpoints():
    r1 = client.get("/api/v1/index/overview")
    assert r1.status_code == 200
    assert "current_apix" in r1.json()

    r2 = client.get("/api/v1/routes")
    assert r2.status_code == 200
    assert len(r2.json()) == 10

    r3 = client.get("/api/v1/lead-time")
    assert r3.status_code == 200
    assert len(r3.json()) == 5  # T+1, T+7, T+15, T+30, T+45

    r4 = client.get("/api/v1/data-quality")
    assert r4.status_code == 200
    assert r4.json()["overall_score"] > 80
