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
    def stats(self):
        with self._connect() as con:
            total=con.execute("SELECT COUNT(*) FROM fare_observations").fetchone()[0]
            live=con.execute("SELECT COUNT(*) FROM fare_observations WHERE collection_status='SUCCESS' AND total_fare IS NOT NULL AND total_fare>0").fetchone()[0]
            success=con.execute("SELECT COUNT(*) FROM fare_observations WHERE collection_status='SUCCESS'").fetchone()[0]
            failed=con.execute("SELECT COUNT(*) FROM fare_observations WHERE collection_status='ERROR'").fetchone()[0]
            last_attempt=con.execute("SELECT MAX(collected_at) FROM fare_observations").fetchone()[0]
            last_success=con.execute("SELECT MAX(collected_at) FROM fare_observations WHERE collection_status='SUCCESS'").fetchone()[0]
            return {"audit_records":total,"live_observations":live,"success_count":success,"failure_count":failed,"last_attempt":last_attempt,"last_success":last_success}
    def source_stats(self, source_id):
        with self._connect() as con:
            row=con.execute("SELECT COUNT(*) total, SUM(CASE WHEN collection_status='SUCCESS' AND total_fare>0 THEN 1 ELSE 0 END) live, SUM(CASE WHEN collection_status='SUCCESS' THEN 1 ELSE 0 END) success, SUM(CASE WHEN collection_status='ERROR' THEN 1 ELSE 0 END) failed, MAX(collected_at) last_attempt, MAX(CASE WHEN collection_status='SUCCESS' THEN collected_at END) last_success FROM fare_observations WHERE source_id=?",(source_id,)).fetchone()
            return dict(row)
    def live_routes(self):
        with self._connect() as con:
            return con.execute("SELECT COUNT(DISTINCT origin||'-'||destination) FROM fare_observations WHERE collection_status='SUCCESS' AND total_fare>0").fetchone()[0]

    def query(self, origin=None,destination=None,start=None,end=None,limit=5000):
        where=[]; args=[]
        if origin:where.append('origin=?');args.append(origin)
        if destination:where.append('destination=?');args.append(destination)
        if start:where.append('travel_date>=?');args.append(start)
        if end:where.append('travel_date<=?');args.append(end)
        q='SELECT * FROM fare_observations'+((' WHERE '+' AND '.join(where)) if where else '')+' ORDER BY collected_at DESC LIMIT ?';args.append(limit)
        with self._connect() as con:return [dict(r) for r in con.execute(q,args)]
