from __future__ import annotations
import math, statistics
from collections import Counter

def iqr_flags(values: list[float], factor: float = 1.5):
    if len(values) < 4:
        return [False] * len(values)
    xs = sorted(values)
    q1 = xs[(len(xs) - 1) // 4]
    q3 = xs[3 * (len(xs) - 1) // 4]
    iqr = q3 - q1
    if iqr == 0:
        return [False] * len(values)
    lo, hi = q1 - factor * iqr, q3 + factor * iqr
    return [x < lo or x > hi for x in values]

def robust_mad_flags(values: list[float], threshold: float = 3.5):
    if len(values) < 4:
        return [False] * len(values)
    med = statistics.median(values)
    dev = [abs(x - med) for x in values]
    mad = statistics.median(dev)
    if mad == 0:
        return [False] * len(values)
    return [0.6745 * abs(x - med) / mad > threshold for x in values]

def observation_identity_key(r: dict) -> tuple:
    """
    Returns the canonical identity key for a single observation event.
    
    True Duplicate Semantics:
    Two observations are TRUE DUPLICATES if and only if they represent the
    same flight offer observed by the same provider at the exact same collection event:
      (source_id, origin, destination, airline, flight_identifier, travel_date, fare_class, collection_timestamp)
      
    Legitimate Repeated Observations:
    - Same flight observed at a DIFFERENT collection_timestamp (time-series price tracking) -> NOT a duplicate.
    - Same flight operating on a DIFFERENT travel_date -> NOT a duplicate.
    - Competing airlines/flights on the same route and same collection time -> NOT duplicates.
    """
    source = r.get('source_id') or r.get('provider_id') or 'UNKNOWN'
    origin = r.get('origin') or (r.get('route_id', '-').split('-')[0] if '-' in r.get('route_id', '') else '')
    dest = r.get('destination') or (r.get('route_id', '-').split('-')[1] if '-' in r.get('route_id', '') else '')
    airline = r.get('airline') or ''
    flight = r.get('flight_number') or r.get('flight_id') or ''
    travel_date = str(r.get('travel_date') or '')
    fare_class = r.get('fare_class') or 'Economy'
    collected_at = str(r.get('collected_at') or r.get('observation_timestamp') or '')
    return (source, origin, dest, airline, flight, travel_date, fare_class, collected_at)

def quality_summary(records: list[dict], attempted: int | None = None) -> dict:
    n = len(records)
    if not n:
        return {
            "overall_score": 0.0,
            "completeness": 0.0,
            "duplicate_rate": 0.0,
            "missing_fare_rate": 0.0,
            "outlier_rate": 0.0,
            "collection_success_rate": 0.0 if attempted else None,
            "last_updated": None,
            "scoring_explanation": "Score = 100 - 3.0×(Missing Rate) - 0.5×(Duplicate Rate) - 1.2×(Outlier Rate)",
            "true_duplicate_count": 0,
            "total_observations": 0
        }
    fares = [float(r.get('total_fare') or 0) for r in records]
    missing = sum(x <= 0 for x in fares)
    flags_i = iqr_flags([x for x in fares if x > 0])
    flags_m = robust_mad_flags([x for x in fares if x > 0])
    out = sum(a or b for a, b in zip(flags_i, flags_m)) if flags_i else 0
    
    keys = [observation_identity_key(r) for r in records]
    dup = n - len(set(keys))
    
    completeness = 100.0 * (1.0 - missing / n)
    duplicate_rate = 100.0 * dup / n
    missing_rate = 100.0 * missing / n
    outlier_rate = 100.0 * out / n
    success = 100.0 * (n / attempted) if attempted else None
    
    score = max(0.0, min(100.0, 100.0 - 3.0 * missing_rate - 0.5 * duplicate_rate - 1.2 * outlier_rate))
    
    return {
        "overall_score": round(score, 2),
        "completeness": round(completeness, 2),
        "duplicate_rate": round(duplicate_rate, 2),
        "missing_fare_rate": round(missing_rate, 2),
        "outlier_rate": round(outlier_rate, 2),
        "collection_success_rate": round(success, 2) if success is not None else None,
        "last_updated": records[0].get('collected_at') if records else None,
        "scoring_explanation": "Score = 100 - 3.0×(Missing Rate) - 0.5×(Duplicate Rate) - 1.2×(Outlier Rate)",
        "true_duplicate_count": dup,
        "total_observations": n
    }
