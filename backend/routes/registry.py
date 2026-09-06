from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Route:
    route_id: str
    origin: str
    destination: str
    origin_name: str
    destination_name: str
    dgca_traffic_weight: float
    weight_status: str = "DGCA_READY_TEMPLATE"

ROUTES = [
    Route("DEL-BOM","DEL","BOM","Delhi","Mumbai",0.14),
    Route("BOM-DEL","BOM","DEL","Mumbai","Delhi",0.14),
    Route("DEL-BLR","DEL","BLR","Delhi","Bengaluru",0.10),
    Route("BLR-DEL","BLR","DEL","Bengaluru","Delhi",0.10),
    Route("BOM-BLR","BOM","BLR","Mumbai","Bengaluru",0.08),
    Route("BLR-BOM","BLR","BOM","Bengaluru","Mumbai",0.08),
    Route("DEL-HYD","DEL","HYD","Delhi","Hyderabad",0.06),
    Route("HYD-DEL","HYD","DEL","Hyderabad","Delhi",0.06),
    Route("BOM-HYD","BOM","HYD","Mumbai","Hyderabad",0.05),
    Route("HYD-BOM","HYD","BOM","Hyderabad","Mumbai",0.05),
    Route("DEL-MAA","DEL","MAA","Delhi","Chennai",0.04),
    Route("MAA-DEL","MAA","DEL","Chennai","Delhi",0.04),
    Route("BOM-CCU","BOM","CCU","Mumbai","Kolkata",0.03),
    Route("CCU-BOM","CCU","BOM","Kolkata","Mumbai",0.03),
    Route("DEL-CCU","DEL","CCU","Delhi","Kolkata",0.03),
    Route("CCU-DEL","CCU","DEL","Kolkata","Delhi",0.03),
    Route("BOM-GOI","BOM","GOI","Mumbai","Goa",0.02),
    Route("GOI-BOM","GOI","BOM","Goa","Mumbai",0.02),
    Route("DEL-GOI","DEL","GOI","Delhi","Goa",0.02),
    Route("GOI-DEL","GOI","DEL","Goa","Delhi",0.02),
]

# These are pilot weights only. They are deliberately labelled so they cannot be
# mistaken for official DGCA values. Replace them with a verified DGCA export via
# `dgca_route_weights.csv` before a policy-grade release.

def normalized_routes(routes: Iterable[Route] = ROUTES) -> list[Route]:
    routes = list(routes)
    total = sum(max(r.dgca_traffic_weight, 0) for r in routes) or 1.0
    return [Route(r.route_id,r.origin,r.destination,r.origin_name,r.destination_name,r.dgca_traffic_weight/total,r.weight_status) for r in routes]

def get_route(origin: str, destination: str) -> Route | None:
    origin, destination = origin.upper(), destination.upper()
    return next((r for r in ROUTES if r.origin == origin and r.destination == destination), None)
