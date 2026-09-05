from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date

class FareBreakdown(BaseModel):
    base_fare: float
    taxes: float
    airport_fee: float
    convenience_fee: float
    other_fee: float = 0.0
    total_fare: float

class ProviderOffer(BaseModel):
    provider_id: str
    provider_name: str
    is_direct: bool = False
    base_fare: float
    taxes: float
    fees: float
    total_fare: float
    currency: str = "INR"
    last_checked_minutes_ago: int = 2
    is_cheapest: bool = False
    is_best_value: bool = False
    breakdown: FareBreakdown

class FlightCard(BaseModel):
    flight_id: str
    airline_code: str
    airline_name: str
    flight_number: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    stops_text: str = "Non-stop"
    cabin_class: str = "Economy"
    cheapest_fare: float
    offers: List[ProviderOffer]

class SearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    adults: int = 1
    children: int = 0
    infants: int = 0
    cabin: str = "Economy"

class SearchResponse(BaseModel):
    origin: str
    destination: str
    travel_date: str
    total_flights: int
    flights: List[FlightCard]

class RawObservation(BaseModel):
    id: str
    timestamp: str
    origin: str
    destination: str
    airline: str
    flight_number: str
    provider: str
    departure_datetime: str
    arrival_datetime: str
    lead_time_days: int
    fare_class: str
    base_fare: float
    taxes: float
    airport_fee: float
    convenience_fee: float
    other_fee: float
    total_fare: float
    currency: str = "INR"
    availability_status: str = "AVAILABLE"  # AVAILABLE, SOLD_OUT, CANCELLED
    source_type: str = "SYNTHETIC_DEMO"
    collection_status: str = "SUCCESS"
    raw_reference: str

class CleanedObservation(BaseModel):
    route_id: str
    flight_id: str
    provider_id: str
    observation_timestamp: str
    travel_date: str
    lead_time: int  # 1, 7, 15, 30, 45
    airline: str
    fare_class: str
    base_fare: float
    taxes: float
    fees: float
    total_fare: float
    currency: str = "INR"
    availability: str = "AVAILABLE"
    quality_score: float
    outlier_flag: bool = False

class RouteBasketItem(BaseModel):
    route_id: str  # e.g., DEL-BOM
    origin: str
    destination: str
    origin_name: str
    destination_name: str
    passenger_traffic_annual: int
    traffic_share: float
    weight: float
    enabled: bool = True
    total_observations: int
    avg_fare: float

class IndexValue(BaseModel):
    period: str  # e.g., "2026-09-04" or "2026-09"
    index_value: float
    base_period: str = "2026-01"
    base_index: float = 100.0
    daily_change_pct: float
    weekly_change_pct: float
    monthly_change_pct: float
    total_routes: int
    total_observations: int
    methodology_version: str = "1.0"

class LeadTimePoint(BaseModel):
    lead_time: str  # T+1, T+7, T+15, T+30, T+45
    days: int
    avg_fare: float
    indigo_fare: float
    airindia_fare: float
    akasa_fare: float
    spicejet_fare: float

class HeatmapItem(BaseModel):
    route_id: str
    origin: str
    destination: str
    current_avg_fare: float
    prev_avg_fare: float
    change_pct: float
    traffic_weight: float
    intensity: str  # HIGH_INCREASE, MODERATE_INCREASE, STABLE, DECREASE

class AirlineMetric(BaseModel):
    airline_name: str
    code: str
    avg_fare: float
    median_fare: float
    cheapest_fare: float
    highest_fare: float
    volatility: str  # Low, Medium, High
    volatility_score: float
    route_coverage: int

class OTAMetric(BaseModel):
    provider_name: str
    avg_price_diff_pct: float
    availability_rate: float
    fee_avg: float
    fare_consistency_score: float

class DataQualityMetrics(BaseModel):
    overall_score: float = 94.0
    completeness: float = 97.2
    duplicate_rate: float = 1.2
    missing_fare_rate: float = 0.8
    outlier_rate: float = 2.1
    collection_success_rate: float = 96.5
    last_updated: str

class CollectionJobStatus(BaseModel):
    provider_name: str
    status: str  # Healthy, Warning, Failed
    last_run: str
    success_rate: float
    error_count: int

from typing import List, Optional, Dict, Any, Union

class BacktestResult(BaseModel):
    start_date: str
    end_date: str
    routes_count: int
    apix_mean: float
    benchmark_mean: float
    mae: float
    rmse: float
    pearson_correlation: float
    data_points: List[Dict[str, Any]]

class MethodologyConfig(BaseModel):
    version: str = "1.0"
    base_period: str = "January 2026"
    base_index: float = 100.0
    formula_type: str = "Weighted Laspeyres Aggregation"
    outlier_threshold_iqr: float = 1.5
    lead_time_windows: List[int] = [1, 7, 15, 30, 45]
    missing_data_treatment: str = "Linear Interpolation & Forward Carry"
