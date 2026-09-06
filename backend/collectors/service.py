from __future__ import annotations
import asyncio
from datetime import date
from pathlib import Path
from collectors.base import CollectionRequest
from collectors.official_routes import PublicRouteFareCollector, AIRLINE_SOURCES
from collectors.ota_adapters import OTACollector, OTA_SOURCES
from storage.observations import ObservationStore

REGISTRY={**{k:PublicRouteFareCollector(k) for k in AIRLINE_SOURCES}, **{k:OTACollector(k) for k in OTA_SOURCES}}

class CollectionService:
    def __init__(self, store: ObservationStore | None=None): self.store=store or ObservationStore()
    async def collect_one(self, source_id: str, origin: str, destination: str, travel_date: str, adults: int=1, cabin: str="Economy", lead_time_days: int|None=None):
        if source_id not in REGISTRY: raise ValueError(f"Unknown source_id {source_id}")
        req=CollectionRequest(origin.upper(),destination.upper(),date.fromisoformat(travel_date),adults,cabin,lead_time_days)
        obs=await REGISTRY[source_id].collect(req)
        inserted=self.store.insert_many(obs)
        return {"inserted":inserted,"observations":obs}
    def collect_one_sync(self,*args,**kwargs): return asyncio.run(self.collect_one(*args,**kwargs))
