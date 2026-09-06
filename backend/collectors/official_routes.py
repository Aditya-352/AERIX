from __future__ import annotations
from datetime import datetime, date
from collectors.base import FareCollector, CollectionRequest, FareObservation
from collectors.compliance import assert_robots_allowed, ComplianceBlocked
from collectors.http import fetch_page
from collectors.parsers import money, snapshot_hash
from config.settings import settings

AIRLINE_SOURCES={
    "INDIGO_PUBLIC_ROUTE": {"name":"IndiGo","type":"AIRLINE_DIRECT","template":"https://www.goindigo.in/domestic-flights/{origin_slug}-to-{destination_slug}-flights.html","status":"LIVE_PUBLIC_ADAPTER"},
    "AIR_INDIA_PUBLIC_ROUTE": {"name":"Air India","type":"AIRLINE_DIRECT","template":"https://www.airindia.com/en-in/book-flights/{origin_slug}-to-{destination_slug}-flights","status":"ADAPTER_PENDING"},
    "AIR_INDIA_EXPRESS_PUBLIC_ROUTE": {"name":"Air India Express","type":"AIRLINE_DIRECT","template":"https://flights.airindiaexpress.com/en-in/{origin_slug}-to-{destination_slug}-flights","status":"LIVE_PUBLIC_ADAPTER"},
    "AKASA_PUBLIC_ROUTE": {"name":"Akasa Air","type":"AIRLINE_DIRECT","template":"https://www.akasaair.com/{origin_slug}-to-{destination_slug}-flights","status":"ADAPTER_PENDING"},
    "SPICEJET_PUBLIC_ROUTE": {"name":"SpiceJet","type":"AIRLINE_DIRECT","template":"https://www.spicejet.com/","status":"ADAPTER_PENDING"},
}
SLUGS={"DEL":"delhi","BOM":"mumbai","BLR":"bengaluru","CCU":"kolkata","HYD":"hyderabad","MAA":"chennai","GOI":"goa","PNQ":"pune","AMD":"ahmedabad","COK":"kochi","JAI":"jaipur","LKO":"lucknow"}

class PublicRouteFareCollector(FareCollector):
    def __init__(self, source_id: str):
        self.source_id=source_id; meta=AIRLINE_SOURCES[source_id]
        self.source_name=meta["name"]; self.source_type=meta["type"]; self.status=meta.get("status","LIVE_PUBLIC_ADAPTER")
        self.source_granularity="DATE_LEVEL_ROUTE_SIGNAL"; self.parser_version="2.1"; self.template=meta["template"]
        self.robots_status="NOT_VERIFIED"; self.authorization_status="PENDING_REVIEW" if self.status!="LIVE_PUBLIC_ADAPTER" else "PUBLIC_SOURCE"
        self.policy="robots.txt + ToS/authorization; no CAPTCHA bypass"
    def url(self, request):
        o=SLUGS.get(request.origin,request.origin.lower()); d=SLUGS.get(request.destination,request.destination.lower())
        return self.template.format(origin_slug=o,destination_slug=d)
    async def collect(self, request: CollectionRequest):
        url=self.url(request)
        try:
            assert_robots_allowed(url, settings.user_agent)
            title,text=await fetch_page(url)
            fare=None
            target_tokens=[request.travel_date.strftime('%d %b %Y'), request.travel_date.strftime('%d %B %Y'), request.travel_date.strftime('%b %d')]
            lines=[x.strip() for x in text.splitlines() if x.strip()]
            for i,line in enumerate(lines):
                if any(tok.lower() in line.lower() for tok in target_tokens) and ("₹" in line or "INR" in line):
                    fare=money(line) or (money(lines[i+1]) if i+1<len(lines) else None)
                    if fare: break
            if fare is None:
                candidates=[money(l) for l in lines if ("Economy" in l or "From INR" in l or "LOWEST PRICE" in l or "Fare" in l) and money(l)]
                fare=min(candidates) if candidates else None
            if fare is None: raise RuntimeError(f"No parseable public fare found on {url}")
            now=datetime.utcnow().isoformat()+"Z"; lead=request.lead_time_days if request.lead_time_days is not None else max((request.travel_date-date.today()).days,0)
            return [FareObservation(self.source_id,self.source_name,self.source_type,"DATE_LEVEL_ROUTE_SIGNAL",now,request.travel_date.isoformat(),request.origin,request.destination,self.source_name,"","Economy","INR",fare,None,None,None,None,fare,"AVAILABLE",lead,url,snapshot_hash(text),snapshot_hash(text)[:16],self.parser_version,"ROBOTS_ALLOWED","SUCCESS")]
        except Exception as exc:
            return [self.error_observation(request,url,exc,"BLOCKED" if isinstance(exc,ComplianceBlocked) else "NOT_VERIFIED")]
