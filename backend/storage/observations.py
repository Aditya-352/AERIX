from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable
from collectors.base import FareObservation

class ObservationStore:
    def __init__(self,path: str|Path="data/aerova_live.db"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self._init()
    def _connect(self):
        con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row; return con
    def _init(self):
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS fare_observations(
            id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, source_name TEXT NOT NULL,
            source_type TEXT NOT NULL, source_granularity TEXT NOT NULL, collected_at TEXT NOT NULL,
            travel_date TEXT NOT NULL, origin TEXT NOT NULL, destination TEXT NOT NULL, airline TEXT,
            flight_number TEXT, fare_class TEXT, currency TEXT NOT NULL, base_fare REAL, taxes REAL,
            airport_fee REAL, convenience_fee REAL, other_fee REAL, total_fare REAL, availability_status TEXT NOT NULL,
            lead_time_days INTEGER, source_url TEXT NOT NULL, raw_reference TEXT, raw_snapshot_hash TEXT,
            parser_version TEXT NOT NULL, compliance_status TEXT NOT NULL, collection_status TEXT NOT NULL, error TEXT,
            UNIQUE(source_id, travel_date, origin, destination, collected_at, raw_reference))""")
            con.execute("CREATE INDEX IF NOT EXISTS ix_fare_route_date ON fare_observations(origin,destination,travel_date,collected_at)")
            con.execute("CREATE INDEX IF NOT EXISTS ix_fare_source ON fare_observations(source_id,collected_at)")
    def insert_many(self, observations: Iterable[FareObservation])->int:
        rows=[o.to_dict() for o in observations]
        if not rows:return 0
        cols=list(rows[0].keys()); placeholders=','.join(':'+c for c in cols)
        sql=f"INSERT OR IGNORE INTO fare_observations ({','.join(cols)}) VALUES ({placeholders})"
        with self._connect() as con:
            before=con.total_changes; con.executemany(sql,rows); con.commit(); return con.total_changes-before
    def recent(self,limit=100):
        with self._connect() as con:return [dict(r) for r in con.execute("SELECT * FROM fare_observations ORDER BY collected_at DESC LIMIT ?",(limit,))]
    def query(self, origin=None,destination=None,start=None,end=None,limit=5000):
        where=[]; args=[]
        if origin:where.append('origin=?');args.append(origin)
        if destination:where.append('destination=?');args.append(destination)
        if start:where.append('travel_date>=?');args.append(start)
        if end:where.append('travel_date<=?');args.append(end)
        q='SELECT * FROM fare_observations'+((' WHERE '+' AND '.join(where)) if where else '')+' ORDER BY collected_at DESC LIMIT ?';args.append(limit)
        with self._connect() as con:return [dict(r) for r in con.execute(q,args)]
