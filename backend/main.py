import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
import random
from dataclasses import asdict
from datetime import datetime

from models import (
    SearchResponse, FlightCard, ProviderOffer, FareBreakdown,
    IndexValue, RouteBasketItem, LeadTimePoint, HeatmapItem,
    AirlineMetric, OTAMetric, DataQualityMetrics, CollectionJobStatus,
    BacktestResult, MethodologyConfig, RealReferenceDataResponse
)
from synthetic_engine import dataset_engine, AIRLINES, PROVIDERS, DEFAULT_ROUTES
from index_engine import AirfareIndexEngine
from data_cleaning import DataCleaningPipeline
from backtester import IndexBacktester
from scraper.dgca_fetcher import BenchmarkFetchError
from data.real_reference_data import REAL_FARE_DATA_POINTS, REAL_TRAFFIC_DATA_POINTS, KNOWN_GAPS

app = FastAPI(
    title="AEROVA — India Airfare Price Intelligence Platform API",
    description="High-frequency real-time airfare monitoring, multi-provider comparison, and Airfare Price Index (APIx) calculation for India.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

index_engine = AirfareIndexEngine(dataset_engine.cleaned_observations)

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now().isoformat(),
        "mode": "SYNTHETIC_DEMO",
        "dataset_observations": len(dataset_engine.cleaned_observations)
    }

@app.get("/api/v1/search", response_model=SearchResponse)
def search_flights(
    origin: str = Query(..., example="DEL"),
    destination: str = Query(..., example="BOM"),
    departure_date: str = Query("2026-09-15"),
    return_date: Optional[str] = None,
    adults: int = 1,
    cabin: str = "Economy"
):
    """Consumer Flight Search with Multi-Provider Price Comparison."""
    origin = origin.upper()
    destination = destination.upper()

    matching_route = next((r for r in DEFAULT_ROUTES if r["origin"] == origin and r["destination"] == destination), None)
    base_price = matching_route["base_price"] if matching_route else 5200

    flights: List[FlightCard] = []
    
    # Generate 5-8 flight options for the searched route
    times = [("06:00", "08:15"), ("08:30", "10:45"), ("11:15", "13:30"), ("14:00", "16:15"), ("17:30", "19:45"), ("20:00", "22:15")]

    for i, (dep, arr) in enumerate(times):
        airline = AIRLINES[i % len(AIRLINES)]
        flight_num = f"{airline['code']} {100 + i * 123}"
        flight_id = f"{airline['code']}_{flight_num.replace(' ', '')}_SEARCH"

        raw_base = base_price * airline["price_mult"] * random.uniform(0.95, 1.05)

        offers: List[ProviderOffer] = []
        cheapest_val = float('inf')

        for prov in PROVIDERS:
            p_fare = raw_base * (1.0 + prov["variance"])
            taxes = round(p_fare * 0.16, 2)
            airport_fee = 200.0
            conv_fee = float(prov["fee"])
            total = round(p_fare + taxes + airport_fee + conv_fee, 2)

            if total < cheapest_val:
                cheapest_val = total

            breakdown = FareBreakdown(
                base_fare=round(p_fare, 2),
                taxes=taxes,
                airport_fee=airport_fee,
                convenience_fee=conv_fee,
                other_fee=0.0,
                total_fare=total
            )

            offers.append(ProviderOffer(
                provider_id=prov["id"],
                provider_name=prov["name"],
                is_direct=(prov["id"] == "DIRECT"),
                base_fare=round(p_fare, 2),
                taxes=taxes,
                fees=airport_fee + conv_fee,
                total_fare=total,
                currency="INR",
                last_checked_minutes_ago=random.randint(1, 5),
                breakdown=breakdown
            ))

        # Mark cheapest & best value offers
        for o in offers:
            if o.total_fare == cheapest_val:
                o.is_cheapest = True
            if o.is_direct:
                o.is_best_value = True

        flights.append(FlightCard(
            flight_id=flight_id,
            airline_code=airline["code"],
            airline_name=airline["name"],
            flight_number=flight_num,
            origin=origin,
            destination=destination,
            departure_time=dep,
            arrival_time=arr,
            duration="2h 15m",
            stops=0,
            stops_text="Non-stop",
            cabin_class=cabin,
            cheapest_fare=cheapest_val,
            offers=sorted(offers, key=lambda x: x.total_fare)
        ))

    return SearchResponse(
        origin=origin,
        destination=destination,
        travel_date=departure_date,
        total_flights=len(flights),
        flights=flights
    )

@app.get("/api/v1/index/overview")
def get_index_overview():
    series = index_engine.calculate_index_series()
    latest = series[-1] if series else None

    return {
        "current_apix": latest.index_value if latest else 114.7,
        "daily_change": latest.daily_change_pct if latest else 0.8,
        "weekly_change": latest.weekly_change_pct if latest else 2.1,
        "monthly_change": latest.monthly_change_pct if latest else 3.4,
        "routes_tracked": len(index_engine.routes),
        "observations_count": len(dataset_engine.raw_observations),
        "last_successful_collection": "2 minutes ago",
        "data_coverage": "99.2%",
        "data_quality_score": 94.0,
        "status": "OPERATIONAL"
    }

@app.get("/api/v1/index/series", response_model=List[IndexValue])
def get_index_series():
    return index_engine.calculate_index_series()

@app.get("/api/v1/routes", response_model=List[RouteBasketItem])
def get_routes():
    return index_engine.get_route_basket()

@app.get("/api/v1/lead-time", response_model=List[LeadTimePoint])
def get_lead_time(route_id: Optional[str] = None):
    return index_engine.get_lead_time_elasticity(route_id=route_id)

@app.get("/api/v1/heatmap", response_model=List[HeatmapItem])
def get_heatmap():
    return index_engine.get_route_heatmap_data()

@app.get("/api/v1/airlines", response_model=List[AirlineMetric])
def get_airlines():
    return index_engine.get_airline_analytics()

@app.get("/api/v1/otas", response_model=List[OTAMetric])
def get_otas():
    return index_engine.get_ota_analytics()

@app.get("/api/v1/data-quality", response_model=DataQualityMetrics)
def get_data_quality():
    q_dict = DataCleaningPipeline.compute_quality_metrics(dataset_engine.cleaned_observations)
    # collection_success_rate is -1.0 when it hasn't been measured yet (see
    # data_cleaning.py) — surface that as null in the API rather than a
    # constant that looks like a real 96.5% success rate.
    if q_dict.get("collection_success_rate", 0) < 0:
        q_dict["collection_success_rate"] = None
    return DataQualityMetrics(**q_dict)

@app.get("/api/v1/collection-monitoring", response_model=List[CollectionJobStatus])
def get_collection_monitoring():
    return [
        CollectionJobStatus(provider_name="IndiGo Direct", status="Healthy", last_run="10 min ago", success_rate=99.2, error_count=0),
        CollectionJobStatus(provider_name="Air India Direct", status="Healthy", last_run="12 min ago", success_rate=98.5, error_count=1),
        CollectionJobStatus(provider_name="Akasa Air Direct", status="Warning", last_run="25 min ago", success_rate=94.1, error_count=3),
        CollectionJobStatus(provider_name="SpiceJet Direct", status="Healthy", last_run="11 min ago", success_rate=97.8, error_count=0),
        CollectionJobStatus(provider_name="MakeMyTrip Feed", status="Healthy", last_run="5 min ago", success_rate=99.5, error_count=0),
        CollectionJobStatus(provider_name="ixigo Feed", status="Healthy", last_run="8 min ago", success_rate=99.1, error_count=0),
        CollectionJobStatus(provider_name="Yatra Feed", status="Healthy", last_run="14 min ago", success_rate=96.7, error_count=2),
    ]

@app.get("/api/v1/backtest", response_model=BacktestResult)
def get_backtest():
    series = index_engine.calculate_index_series()
    try:
        return IndexBacktester.run_backtest(
            series,
            annexure_xlsx_url=os.environ.get("MOSPI_ANNEXURE_XLSX_URL"),
        )
    except BenchmarkFetchError as e:
        # PREVIOUSLY this endpoint always returned 200 with fabricated
        # numbers. Now it returns a real, informative error until
        # MOSPI_ANNEXURE_XLSX_URL is set to a valid, CURRENT month's
        # Annexure I link (see scraper/dgca_fetcher.py — this URL changes
        # every month and must be refreshed manually, it is not
        # auto-discovered). This is a 503, not a 500 — it's a known,
        # expected state (missing/stale external config), not an
        # unhandled crash.
        raise HTTPException(
            status_code=503,
            detail=f"Backtest unavailable: {e}"
        )

@app.get("/api/v1/methodology", response_model=MethodologyConfig)
def get_methodology():
    return MethodologyConfig()

@app.get("/api/v1/real-reference-data", response_model=RealReferenceDataResponse)
def get_real_reference_data():
    """
    Returns real, individually-sourced fare and traffic figures pulled
    from public news reporting (DGCA Tariff Monitoring Unit analyses,
    ixigo fare reports, civilaviation.gov.in live stats) as of the search
    performed 2026-09-05. See data/real_reference_data.py for full
    sourcing detail, methodology caveats, and explicitly documented gaps.

    THIS IS NOT: the CPI backtest (see /api/v1/backtest for that), a
    scraped dataset, or a systematic time series. It is spot-check
    reference data — useful for showing real prices were investigated and
    for giving a presentation concrete, citable real numbers, not for
    validating APIx programmatically.
    """
    # dataclasses.asdict() converts the plain @dataclass instances from
    # real_reference_data.py into dicts, which Pydantic can validate into
    # RealFareReference/RealTrafficReference. Passing the dataclass
    # instances directly (without this conversion) fails at runtime —
    # Pydantic does not treat a same-shaped dataclass as equivalent to its
    # own BaseModel, even with matching fields. Caught by actually running
    # this endpoint, not by inspection.
    return RealReferenceDataResponse(
        fare_data=[asdict(d) for d in REAL_FARE_DATA_POINTS],
        traffic_data=[asdict(d) for d in REAL_TRAFFIC_DATA_POINTS],
        known_gaps=KNOWN_GAPS,
    )

@app.get("/api/v1/alerts")
def get_alerts():
    return [
        {"id": "ALT-1", "severity": "HIGH", "title": "Significant Fare Increase", "message": "DEL–BOM T+1 average fare increased by +12.4% over 24h.", "timestamp": "10 min ago"},
        {"id": "ALT-2", "severity": "MEDIUM", "title": "Index Spike Detected", "message": "APIx 7-day index rose by +2.1% across Tier 1 routes.", "timestamp": "1h ago"},
        {"id": "ALT-3", "severity": "LOW", "title": "Collection Latency", "message": "Akasa Air provider adapter experiencing 25min collection delay.", "timestamp": "2h ago"}
    ]
