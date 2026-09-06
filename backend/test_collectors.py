import asyncio
from datetime import date

from collectors.indigo import IndigoPublicRouteCollector
from collectors.base import CollectionRequest


def test_indigo_route_url():
    c = IndigoPublicRouteCollector()
    req = CollectionRequest("DEL", "BOM", date(2026, 9, 20))
    assert c.route_url(req).endswith("/domestic-flights/delhi-to-mumbai-flights.html")


def test_indigo_price_parser():
    text = "Delhi to Mumbai flight\nLOWEST PRICE\n₹5,943"
    assert IndigoPublicRouteCollector._extract_lowest_price(text) == 5943.0


def test_indigo_average_price_parser():
    text = "Average Price | Economy: ₹5,943 Stretch|Business: ₹21,159"
    assert IndigoPublicRouteCollector._extract_lowest_price(text) == 5943.0
