from __future__ import annotations
import asyncio
from datetime import date
from collectors.base import CollectionRequest, FareCollector
from collectors.official_routes import PublicRouteFareCollector, AIRLINE_SOURCES
from collectors.ota_adapters import OTACollector, OTA_SOURCES
from storage.observations import ObservationStore

SIH_AIRLINES = {
    "INDIGO_PUBLIC_ROUTE", "AIR_INDIA_PUBLIC_ROUTE", "AIR_INDIA_EXPRESS_PUBLIC_ROUTE",
    "AKASA_PUBLIC_ROUTE", "SPICEJET_PUBLIC_ROUTE",
}
SIH_OTAS = {
    "MMT_AUTHORIZED", "YATRA_PUBLIC", "EASEMYTRIP_PUBLIC", "CLEARTRIP_AUTHORIZED",
    "IXIGO_AUTHORIZED", "GOIBIBO_AUTHORIZED",
}

class PendingCollector(FareCollector):
    def __init__(self, meta: dict):
        self.source_id=meta["source_id"]; self.source_name=meta["name"]; self.source_type=meta["type"]
        self.source_granularity=meta.get("source_granularity","DATE_LEVEL_ROUTE_SIGNAL")
        self.parser_version=meta.get("parser_version","2.1")
        self.status=meta.get("status","ADAPTER_PENDING")
        self.robots_status=meta.get("robots_status","NOT_VERIFIED")
        self.authorization_status=meta.get("authorization_status","REQUIRED")
        self.policy=meta.get("policy","robots.txt + ToS/authorization; no CAPTCHA bypass")
    async def collect(self, request: CollectionRequest):
        reason = ("AUTHORIZED_FEED_REQUIRED" if self.status=="AUTHORIZED_FEED_REQUIRED"
                  else "ADAPTER_PENDING")
        return [self.error_observation(request, "", RuntimeError(reason), "NOT_VERIFIED")]

REGISTRY: dict[str, FareCollector] = {}
for sid, meta in AIRLINE_SOURCES.items():
    REGISTRY[sid] = PublicRouteFareCollector(sid) if meta.get("status")=="LIVE_PUBLIC_ADAPTER" else PendingCollector({**meta,"source_id":sid})
for sid, meta in OTA_SOURCES.items():
    REGISTRY[sid] = OTACollector(sid) if meta.get("status")=="LIVE_PUBLIC_ADAPTER" else PendingCollector({**meta,"source_id":sid})

class CollectionService:
    def __init__(self, store: ObservationStore|None=None): self.store=store or ObservationStore()
    async def collect_one(self, source_id: str, origin: str, destination: str, travel_date: str, adults: int=1, cabin: str="Economy", lead_time_days: int|None=None):
        if source_id not in REGISTRY: raise ValueError(f"Unknown source_id {source_id}")
        req=CollectionRequest(origin.upper(),destination.upper(),date.fromisoformat(travel_date),adults,cabin,lead_time_days)
        obs=await REGISTRY[source_id].collect(req)
        inserted=self.store.insert_many(obs)
        return {"inserted":inserted,"observations":obs}
    def collect_one_sync(self,*args,**kwargs): return asyncio.run(self.collect_one(*args,**kwargs))

