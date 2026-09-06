from __future__ import annotations
from datetime import date,timedelta,datetime
import random
from routes.registry import ROUTES

AIRLINES=[{"code":"6E","name":"IndiGo","price_mult":1.00},{"code":"AI","name":"Air India","price_mult":1.08},{"code":"IX","name":"Air India Express","price_mult":0.94},{"code":"QP","name":"Akasa Air","price_mult":0.98},{"code":"SG","name":"SpiceJet","price_mult":0.96}]
PROVIDERS=[{"id":"DIRECT","name":"Airline Direct","variance":0.0,"fee":0},{"id":"YATRA","name":"Yatra","variance":0.006,"fee":149},{"id":"EMT","name":"EaseMyTrip","variance":-0.004,"fee":99},{"id":"CLEARTRIP","name":"Cleartrip","variance":0.008,"fee":149},{"id":"IXIGO","name":"ixigo","variance":-0.002,"fee":129},{"id":"GOIBIBO","name":"Goibibo","variance":0.005,"fee":149},{"id":"MMT","name":"MakeMyTrip","variance":0.007,"fee":149}]

class SyntheticDataEngine:
    def __init__(self,days_history=90):
        random.seed(42); self.raw_observations=[];self.cleaned_observations=[]; self._generate(days_history)
    def _generate(self,days):
        obs_id=0; today=date(2026,9,6)
        for offset in range(days,0,-1):
            d=today-timedelta(days=offset)
            for route in ROUTES:
                for airline in AIRLINES:
                    for lead in (1,7,15,30,45):
                        obs_id+=1
                        # deterministic, plausible research/demo data; explicitly source_type DEMO.
                        base=5600*(1+0.08*((d.weekday() in [4,6]))) * airline['price_mult'] * (1.18 if lead==1 else 1.08 if lead==7 else 1.0 if lead==15 else 0.94 if lead==30 else 0.91)
                        base*=random.uniform(.97,1.03)
                        fees=200+149
                        total=round(base*1.16+fees,2)
                        self.cleaned_observations.append({"route_id":route.route_id,"flight_id":f"{airline['code']}-{obs_id}","provider_id":"DIRECT","observation_timestamp":d.isoformat(),"travel_date":(d+timedelta(days=lead)).isoformat(),"lead_time":lead,"airline":airline['name'],"fare_class":"Economy","base_fare":round(base,2),"taxes":round(base*.16,2),"fees":fees,"total_fare":total,"currency":"INR","availability":"AVAILABLE","quality_score":98.0,"outlier_flag":False,"source_type":"SYNTHETIC_DEMO","source_granularity":"FLIGHT_LEVEL"})

dataset_engine=SyntheticDataEngine()
