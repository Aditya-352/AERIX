from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class FareBreakdown(BaseModel):
    base_fare: float
    taxes: float
    airport_fee: float=0
    convenience_fee: float=0
    other_fee: float=0
    total_fare: float

class ProviderOffer(BaseModel):
    provider_id: str
    provider_name: str
    is_direct: bool=False
    base_fare: float
    taxes: float
    fees: float
    total_fare: float
    currency: str="INR"
    last_checked_minutes_ago: Optional[int]=None
    is_cheapest: bool=False
    is_best_value: bool=False
    breakdown: FareBreakdown
    source_status: str="DEMO"

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
    stops_text: str="Non-stop"
    cabin_class: str="Economy"
    cheapest_fare: float
    offers: List[ProviderOffer]
    data_confidence: str="DEMO"

class SearchResponse(BaseModel):
    origin: str; destination: str; travel_date: str; total_flights: int; flights: List[FlightCard]; data_mode: str; last_updated: str

class IndexPoint(BaseModel):
    period: str; index_value: float; base_period: str; base_index: float=100; daily_change_pct: float; weekly_change_pct: float; monthly_change_pct: float; total_routes: int; total_observations: int; methodology_version: str

class RouteBasketItem(BaseModel):
    route_id: str; origin: str; destination: str; origin_name: str; destination_name: str; passenger_traffic_annual: Optional[int]; traffic_share: float; weight: float; enabled: bool=True; total_observations: int=0; avg_fare: float=0; weight_status: str

class LeadTimePoint(BaseModel):
    lead_time: str; days: int; avg_fare: Optional[float]; observations: int

class HeatmapItem(BaseModel):
    route_id: str; origin: str; destination: str; current_avg_fare: float; prev_avg_fare: float; change_pct: float; traffic_weight: float; intensity: str

class BacktestResponse(BaseModel):
    status: str; message: str; result: Optional[Dict[str,Any]]=None

class MethodologyConfig(BaseModel):
    version: str="2.0"; base_period: str="2024-01"; base_index: float=100; formula_type: str="Fixed-base weighted arithmetic mean of route average fares"; route_weight_source: str="DGCA TMU/official traffic file"; outlier_methods: List[str]=["IQR","MAD"]
    lead_time_windows: List[int]=[1,7,15,30,45]; missing_data_treatment: str="No synthetic imputation; carry only within documented publication rule"

class DataQualityMetrics(BaseModel):
    overall_score: float
    completeness: float
    duplicate_rate: float
    missing_fare_rate: float
    outlier_rate: float
    collection_success_rate: Optional[float] = None
    last_updated: Optional[str] = None
    scoring_explanation: Optional[str] = None
    true_duplicate_count: Optional[int] = None
    total_observations: Optional[int] = None
