from __future__ import annotations
from datetime import date, timedelta, datetime
import math, random, zlib
from routes.registry import ROUTES

AIRLINES = [
    {"code": "6E", "name": "IndiGo", "price_mult": 1.00},
    {"code": "AI", "name": "Air India", "price_mult": 1.08},
    {"code": "IX", "name": "Air India Express", "price_mult": 0.94},
    {"code": "QP", "name": "Akasa Air", "price_mult": 0.98},
    {"code": "SG", "name": "SpiceJet", "price_mult": 0.96},
]
PROVIDERS = [
    {"id": "DIRECT", "name": "Airline Direct", "variance": 0.0, "fee": 0},
    {"id": "YATRA", "name": "Yatra", "variance": 0.006, "fee": 149},
    {"id": "EMT", "name": "EaseMyTrip", "variance": -0.004, "fee": 99},
    {"id": "CLEARTRIP", "name": "Cleartrip", "variance": 0.008, "fee": 149},
    {"id": "IXIGO", "name": "ixigo", "variance": -0.002, "fee": 129},
    {"id": "GOIBIBO", "name": "Goibibo", "variance": 0.005, "fee": 149},
    {"id": "MMT", "name": "MakeMyTrip", "variance": 0.007, "fee": 149},
]

class SyntheticDataEngine:
    def __init__(self, days_history=90, seed=42):
        self.seed = seed
        self.raw_observations = []
        self.cleaned_observations = []
        self._generate(days_history)

    def _generate(self, days):
        rng = random.Random(self.seed)
        obs_id = 0
        today = date(2026, 9, 6)
        state = 0.0
        for offset in range(days, 0, -1):
            d = today - timedelta(days=offset)
            # smooth macro drift + AR(1) volatility + weekend demand effect; deterministic with seed 42.
            state = 0.88 * state + rng.gauss(0, 0.018)
            macro = 1.0 + 0.0007 * (days - offset) + 0.028 * math.sin((d.toordinal() / 28.0)) + state
            weekend = 1.0 + (0.045 if d.weekday() in (4, 6) else 0.0)
            for route in ROUTES:
                route_seed = zlib.crc32(route.route_id.encode()) % 97
                route_factor = 1 + 0.055 * math.sin((route_seed / 97) * math.pi + d.toordinal() / 45.0)
                for airline in AIRLINES:
                    for lead in (1, 7, 15, 30, 45):
                        obs_id += 1
                        lead_mult = {1: 1.18, 7: 1.08, 15: 1.0, 30: 0.94, 45: 0.91}[lead]
                        noise = 1 + rng.gauss(0, 0.012)
                        base = 5600 * macro * route_factor * weekend * airline['price_mult'] * lead_mult * noise
                        base = max(3200, base)
                        fees = 200 + 149
                        total = round(base * 1.16 + fees, 2)
                        record = {
                            "route_id": route.route_id,
                            "flight_id": f"{airline['code']}-{obs_id}",
                            "flight_number": f"{airline['code']} {100 + (obs_id % 899)}",
                            "observation_timestamp": datetime(d.year, d.month, d.day, 10, 0).isoformat() + "Z",
                            "travel_date": (d + timedelta(days=lead)).isoformat(),
                            "lead_time": lead,
                            "lead_time_days": lead,
                            "airline": airline['name'],
                            "fare_class": "Economy",
                            "base_fare": round(base, 2),
                            "taxes": round(base * .16, 2),
                            "airport_fee": 200.0,
                            "convenience_fee": 149.0,
                            "other_fee": 0.0,
                            "fees": fees,
                            "total_fare": total,
                            "currency": "INR",
                            "availability": "AVAILABLE",
                            "availability_status": "AVAILABLE",
                            "quality_score": 98.0,
                            "outlier_flag": False,
                            "source_type": "SYNTHETIC_DEMO",
                            "source_granularity": "FLIGHT_LEVEL",
                            "source_id": "SYNTHETIC_DEMO",
                            "source_name": "Synthetic Research Dataset",
                            "collection_status": "SUCCESS",
                            "compliance_status": "DEMO",
                            "parser_version": "synthetic-2.1",
                            "origin": route.origin,
                            "destination": route.destination,
                            "collected_at": datetime(d.year, d.month, d.day, 10, 0).isoformat() + "Z",
                        }
                        self.cleaned_observations.append(record)
        self.raw_observations = list(self.cleaned_observations)

dataset_engine = SyntheticDataEngine()
