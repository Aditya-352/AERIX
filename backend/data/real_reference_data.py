from dataclasses import dataclass


@dataclass(frozen=True)
class FareReference:
    route_description: str
    fare_inr: float | None
    fare_change_pct: float | None
    period_described: str
    source_name: str
    source_url: str
    article_publish_date: str
    notes: str = ""


@dataclass(frozen=True)
class TrafficReference:
    metric_description: str
    value: str
    period_described: str
    source_name: str
    source_url: str
    article_publish_date: str
    notes: str = ""


# Kept empty until every observation has an auditable source record.
REAL_FARE_DATA_POINTS: list[FareReference] = []
REAL_TRAFFIC_DATA_POINTS: list[TrafficReference] = []
KNOWN_GAPS = (
    "Reference-data tables are intentionally empty in this build rather than "
    "containing unsourced or synthetic values. Populate them only with "
    "individually verified public records."
)
