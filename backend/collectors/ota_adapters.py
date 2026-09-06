from __future__ import annotations
from collectors.base import FareCollector, CollectionRequest
from collectors.official_routes import PublicRouteFareCollector

# OTAs are represented as adapters but must be enabled only where robots.txt/ToS and
# access permissions allow collection. No CAPTCHA bypass or private API harvesting.
OTA_SOURCES={
    "YATRA_PUBLIC": {"name":"Yatra","template":"https://www.yatra.com/flight-schedule/{origin_name}-to-{destination_name}-flights.html"},
    "EASEMYTRIP_PUBLIC": {"name":"EaseMyTrip","template":"https://www.easemytrip.com/flights/{origin}-{origin_iata}-to-{destination}-{destination_iata}/"},
}
class OTACollector(PublicRouteFareCollector):
    source_type="OTA"
    def __init__(self, source_id: str):
        self.source_id=source_id
        meta=OTA_SOURCES[source_id]
        self.source_name=meta["name"]; self.source_type="OTA"
        self.source_granularity="DATE_LEVEL_ROUTE_SIGNAL"; self.parser_version="2.1"
        self.template=meta["template"]
    def url(self, request):
        names={"DEL":"delhi","BOM":"mumbai","BLR":"bangalore","CCU":"kolkata","HYD":"hyderabad","MAA":"chennai","GOI":"goa"}
        o,n=names.get(request.origin,request.origin.lower()), names.get(request.destination,request.destination.lower())
        return self.template.format(origin_name=o,destination_name=n,origin=request.origin.lower(),destination=request.destination.lower(),origin_iata=request.origin.lower(),destination_iata=request.destination.lower())
