from __future__ import annotations
from collectors.official_routes import PublicRouteFareCollector

OTA_SOURCES={
    "MMT_AUTHORIZED": {"name":"MakeMyTrip","type":"OTA","status":"AUTHORIZED_FEED_REQUIRED","template":""},
    "YATRA_PUBLIC": {"name":"Yatra","type":"OTA","status":"LIVE_PUBLIC_ADAPTER","template":"https://www.yatra.com/flight-schedule/{origin_name}-to-{destination_name}-flights.html"},
    "EASEMYTRIP_PUBLIC": {"name":"EaseMyTrip","type":"OTA","status":"LIVE_PUBLIC_ADAPTER","template":"https://www.easemytrip.com/flights/{origin}-{origin_iata}-to-{destination}-{destination_iata}/"},
    "CLEARTRIP_AUTHORIZED": {"name":"Cleartrip","type":"OTA","status":"AUTHORIZED_FEED_REQUIRED","template":""},
    "IXIGO_AUTHORIZED": {"name":"ixigo","type":"OTA","status":"AUTHORIZED_FEED_REQUIRED","template":""},
    "GOIBIBO_AUTHORIZED": {"name":"Goibibo","type":"OTA","status":"AUTHORIZED_FEED_REQUIRED","template":""},
}

class OTACollector(PublicRouteFareCollector):
    def __init__(self, source_id: str):
        self.source_id=source_id; meta=OTA_SOURCES[source_id]
        self.source_name=meta["name"]; self.source_type="OTA"; self.status=meta.get("status","ADAPTER_PENDING")
        self.source_granularity="DATE_LEVEL_ROUTE_SIGNAL"; self.parser_version="2.1"; self.template=meta.get("template","")
        self.robots_status="NOT_VERIFIED"; self.authorization_status="AUTHORIZED_FEED_REQUIRED" if self.status=="AUTHORIZED_FEED_REQUIRED" else "PUBLIC_SOURCE"
        self.policy="robots.txt + ToS/authorization; no CAPTCHA bypass"
    def url(self, request):
        names={"DEL":"delhi","BOM":"mumbai","BLR":"bangalore","CCU":"kolkata","HYD":"hyderabad","MAA":"chennai","GOI":"goa"}
        o,n=names.get(request.origin,request.origin.lower()),names.get(request.destination,request.destination.lower())
        return self.template.format(origin_name=o,destination_name=n,origin=request.origin.lower(),destination=request.destination.lower(),origin_iata=request.origin.lower(),destination_iata=request.destination.lower()) if self.template else ""
