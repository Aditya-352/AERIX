from __future__ import annotations
import hashlib, re
from datetime import datetime
from typing import Iterable

CURRENCY_RE = re.compile(r"(?:INR|₹|Rs\.?|Rs)\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.\d+)?)", re.I)
DATE_RE = re.compile(r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)?[, ]*([0-3]?\d)[ -]([A-Za-z]{3})[ ,'-]?(20\d\d)", re.I)

MONTHS={m.lower():i for i,m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],1)}

def money(text: str) -> float | None:
    m=CURRENCY_RE.search(text)
    return float(m.group(1).replace(',','')) if m else None

def snapshot_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def clean_text(text: str) -> str:
    return re.sub(r"\s+"," ",text).strip()

def parse_flights_from_lines(lines: Iterable[str], requested_date: str, airline_hint: str) -> list[dict]:
    out=[]
    lines=list(lines)
    for i,line in enumerate(lines):
        t=clean_text(line)
        if not re.search(r"\b[0-9]{2}:?[0-9]{2}\b",t) and not re.search(r"\b[A-Z]{2}[- ]?\d{2,5}\b",t):
            continue
        flight=re.search(r"\b([A-Z]{2})[- ]?(\d{2,5})\b",t)
        fare=money(t)
        if not fare and i+1<len(lines): fare=money(lines[i+1])
        if flight and fare:
            out.append({"airline":airline_hint,"flight_number":f"{flight.group(1)}{flight.group(2)}","total_fare":fare})
    return out
