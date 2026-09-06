from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional

@dataclass(frozen=True)
class CollectionRequest:
    origin: str
    destination: str
    travel_date: date
    adults: int = 1
    cabin: str = "Economy"
    lead_time_days: Optional[int] = None

@dataclass(frozen=True)
class FareObservation:
    source_id: str
    source_name: str
    source_type: str
    source_granularity: str
    collected_at: str
    travel_date: str
    origin: str
    destination: str
    airline: str
    flight_number: str
    fare_class: str
    currency: str
    base_fare: Optional[float]
    taxes: Optional[float]
    airport_fee: Optional[float]
    convenience_fee: Optional[float]
    other_fee: Optional[float]
    total_fare: Optional[float]
    availability_status: str
    lead_time_days: int
    source_url: str
    raw_reference: str
    raw_snapshot_hash: str
    parser_version: str
    compliance_status: str
    collection_status: str
    error: Optional[str] = None

    def to_dict(self): return asdict(self)

class FareCollector:
    source_id: str
    source_name: str
    source_type: str
    source_granularity: str = "FLIGHT_LEVEL"
    parser_version: str = "2.0"

    async def collect(self, request: CollectionRequest) -> list[FareObservation]:
        raise NotImplementedError

    def error_observation(self, request: CollectionRequest, url: str, exc: Exception, compliance_status: str="UNKNOWN") -> FareObservation:
        now=datetime.utcnow().isoformat()+"Z"
        return FareObservation(self.source_id,self.source_name,self.source_type,self.source_granularity,now,request.travel_date.isoformat(),request.origin,request.destination,"","","", "INR",None,None,None,None,None,None,"UNKNOWN",request.lead_time_days or max((request.travel_date-date.today()).days,0),url,"", "",self.parser_version,compliance_status,"ERROR",str(exc))
