import random
from datetime import datetime, timedelta
from typing import List, Dict
from models import RawObservation, CleanedObservation, RouteBasketItem

# Representative Domestic Indian Routes with approximate passenger share
DEFAULT_ROUTES = [
    {"route_id": "DEL-BOM", "origin": "DEL", "destination": "BOM", "origin_name": "New Delhi", "destination_name": "Mumbai", "share": 0.085, "base_price": 5400},
    {"route_id": "DEL-BLR", "origin": "DEL", "destination": "BLR", "origin_name": "New Delhi", "destination_name": "Bengaluru", "share": 0.072, "base_price": 5800},
    {"route_id": "BOM-BLR", "origin": "BOM", "destination": "BLR", "origin_name": "Mumbai", "destination_name": "Bengaluru", "share": 0.065, "base_price": 4200},
    {"route_id": "DEL-CCU", "origin": "DEL", "destination": "CCU", "origin_name": "New Delhi", "destination_name": "Kolkata", "share": 0.055, "base_price": 5100},
    {"route_id": "BLR-HYD", "origin": "BLR", "destination": "HYD", "origin_name": "Bengaluru", "destination_name": "Hyderabad", "share": 0.048, "base_price": 3200},
    {"route_id": "MAA-DEL", "origin": "MAA", "destination": "DEL", "origin_name": "Chennai", "destination_name": "New Delhi", "share": 0.046, "base_price": 5900},
    {"route_id": "DEL-HYD", "origin": "DEL", "destination": "HYD", "origin_name": "New Delhi", "destination_name": "Hyderabad", "share": 0.044, "base_price": 4800},
    {"route_id": "BOM-HYD", "origin": "BOM", "destination": "HYD", "origin_name": "Mumbai", "destination_name": "Hyderabad", "share": 0.041, "base_price": 3600},
    {"route_id": "MAA-BOM", "origin": "MAA", "destination": "BOM", "origin_name": "Chennai", "destination_name": "Mumbai", "share": 0.039, "base_price": 4400},
    {"route_id": "BLR-MAA", "origin": "BLR", "destination": "MAA", "origin_name": "Bengaluru", "destination_name": "Chennai", "share": 0.035, "base_price": 2800},
]

AIRLINES = [
    {"code": "6E", "name": "IndiGo", "price_mult": 0.98},
    {"code": "AI", "name": "Air India", "price_mult": 1.05},
    {"code": "QP", "name": "Akasa Air", "price_mult": 0.92},
    {"code": "SG", "name": "SpiceJet", "price_mult": 0.95},
    {"code": "IX", "name": "Air India Express", "price_mult": 0.94},
]

PROVIDERS = [
    {"id": "DIRECT", "name": "Airline Direct", "fee": 0, "variance": 0.0},
    {"id": "MMT", "name": "MakeMyTrip", "fee": 299, "variance": 0.015},
    {"id": "GOIBIBO", "name": "Goibibo", "fee": 249, "variance": 0.010},
    {"id": "IXIGO", "name": "ixigo", "fee": 149, "variance": -0.012},
    {"id": "YATRA", "name": "Yatra", "fee": 279, "variance": 0.008},
    {"id": "EASEMYTRIP", "name": "EaseMyTrip", "fee": 0, "variance": 0.002},
]

LEAD_WINDOWS = [1, 7, 15, 30, 45]

# Lead-time multipliers relative to base fare (T+45 is baseline ~1.0, T+1 is ~1.75x)
LEAD_MULTIPLIERS = {
    1: 1.75,
    7: 1.45,
    15: 1.25,
    30: 1.08,
    45: 1.00
}

class SyntheticDataEngine:
    def __init__(self, days_history: int = 30):
        self.days_history = days_history
        self.raw_observations: List[RawObservation] = []
        self.cleaned_observations: List[CleanedObservation] = []
        self.generate_dataset()

    def generate_dataset(self):
        random.seed(42)  # Deterministic seed for reproducible evaluation
        end_date = datetime(2026, 9, 4)
        start_date = end_date - timedelta(days=self.days_history)

        obs_id = 100000

        for day_offset in range(self.days_history + 1):
            current_obs_date = start_date + timedelta(days=day_offset)
            date_str = current_obs_date.strftime("%Y-%m-%d")

            # Introduce macro index trend (+3.4% inflation over the 30 days)
            macro_factor = 1.0 + (day_offset / self.days_history) * 0.034

            for route in DEFAULT_ROUTES:
                for lead_days in LEAD_WINDOWS:
                    travel_date = current_obs_date + timedelta(days=lead_days)
                    travel_date_str = travel_date.strftime("%Y-%m-%d")

                    for airline in AIRLINES:
                        # 90% chance of flight existing for this combination
                        if random.random() > 0.90:
                            continue

                        flight_num = f"{airline['code']} {random.randint(100, 999)}"
                        dep_hour = random.choice([6, 8, 10, 13, 16, 19, 21])
                        dep_time = f"{dep_hour:02d}:15"
                        arr_hour = (dep_hour + random.choice([2, 3])) % 24
                        arr_time = f"{arr_hour:02d}:25"

                        # Calculate realistic fare
                        base = route["base_price"] * airline["price_mult"] * LEAD_MULTIPLIERS[lead_days] * macro_factor
                        # Add day-of-week variation (weekends +10%)
                        if travel_date.weekday() in [4, 6]:
                            base *= 1.10

                        # Small daily noise
                        base *= random.uniform(0.97, 1.03)

                        for provider in PROVIDERS:
                            obs_id += 1
                            provider_fare_var = base * (1.0 + provider["variance"])
                            taxes = round(provider_fare_var * 0.16, 2)
                            airport_fee = round(random.choice([150, 200, 250]), 2)
                            convenience_fee = float(provider["fee"])
                            total = round(provider_fare_var + taxes + airport_fee + convenience_fee, 2)

                            # 2% outlier rate simulation
                            is_outlier = False
                            if random.random() < 0.02:
                                is_outlier = True
                                total *= random.choice([0.4, 2.5])

                            raw_obs = RawObservation(
                                id=str(obs_id),
                                timestamp=f"{date_str}T08:00:00Z",
                                origin=route["origin"],
                                destination=route["destination"],
                                airline=airline["name"],
                                flight_number=flight_num,
                                provider=provider["name"],
                                departure_datetime=f"{travel_date_str}T{dep_time}:00",
                                arrival_datetime=f"{travel_date_str}T{arr_time}:00",
                                lead_time_days=lead_days,
                                fare_class="Economy",
                                base_fare=round(provider_fare_var, 2),
                                taxes=taxes,
                                airport_fee=airport_fee,
                                convenience_fee=convenience_fee,
                                other_fee=0.0,
                                total_fare=total,
                                currency="INR",
                                availability_status="AVAILABLE",
                                source_type="SYNTHETIC_DEMO",
                                collection_status="SUCCESS",
                                raw_reference=f"REF-{obs_id}"
                            )
                            self.raw_observations.append(raw_obs)

                            cleaned_obs = CleanedObservation(
                                route_id=route["route_id"],
                                flight_id=f"{airline['code']}_{flight_num.replace(' ', '')}_{date_str}_{dep_time}",
                                provider_id=provider["id"],
                                observation_timestamp=date_str,
                                travel_date=travel_date_str,
                                lead_time=lead_days,
                                airline=airline["name"],
                                fare_class="Economy",
                                base_fare=round(provider_fare_var, 2),
                                taxes=taxes,
                                fees=airport_fee + convenience_fee,
                                total_fare=total,
                                currency="INR",
                                availability="AVAILABLE",
                                quality_score=98.5 if not is_outlier else 45.0,
                                outlier_flag=is_outlier
                            )
                            self.cleaned_observations.append(cleaned_obs)

# Singleton global synthetic engine for instant load
dataset_engine = SyntheticDataEngine(days_history=30)
