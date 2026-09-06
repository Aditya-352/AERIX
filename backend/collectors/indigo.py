from collectors.official_routes import PublicRouteFareCollector
from collectors.base import CollectionRequest

class IndigoPublicRouteCollector(PublicRouteFareCollector):
    source_id='INDIGO_PUBLIC_ROUTE'
    source_name='IndiGo Direct — Public Route Page'
    source_type='AIRLINE_DIRECT'
    parser_version='2.1'
    def __init__(self): super().__init__('INDIGO_PUBLIC_ROUTE')
    def route_url(self,request:CollectionRequest): return self.url(request)
    @staticmethod
    def _extract_lowest_price(text):
        from collectors.parsers import money
        import re
        for pat in [r'LOWEST\s+PRICE.{0,250}?₹\s*([0-9][0-9,]*)',r'Average\s+Price.{0,250}?₹\s*([0-9][0-9,]*)',r'Economy\s*:\s*₹\s*([0-9][0-9,]*)']:
            m=re.search(pat,text,flags=re.I|re.S)
            if m:return float(m.group(1).replace(',',''))
        return money(text)
