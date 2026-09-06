from __future__ import annotations
import csv
from pathlib import Path
from routes.registry import Route, ROUTES, normalized_routes

DEFAULT_PATH = Path(__file__).resolve().parent / "dgca_route_weights.csv"

REQUIRED = {"route_id","origin","destination","origin_name","destination_name","passenger_traffic","traffic_share"}

def load_verified_basket(path: str | Path | None = None) -> list[Route]:
    p = Path(path) if path else DEFAULT_PATH
    if not p.exists():
        return normalized_routes(ROUTES)
    rows=[]
    with p.open(newline="", encoding="utf-8") as f:
        reader=csv.DictReader(f)
        missing=REQUIRED-set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"DGCA basket missing columns: {sorted(missing)}")
        for row in reader:
            rows.append(Route(row["route_id"],row["origin"],row["destination"],row["origin_name"],row["destination_name"],float(row["traffic_share"]),"DGCA_FILE_CONFIGURED"))
    if not rows:
        raise ValueError("DGCA route basket file is empty")
    return normalized_routes(rows)
