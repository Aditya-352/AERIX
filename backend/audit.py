from __future__ import annotations
import hashlib,json
from datetime import datetime

def event_hash(payload: dict)->str:
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),default=str).encode()
    return hashlib.sha256(canonical).hexdigest()

def build_audit_record(kind: str, payload: dict, actor="system"):
    now=datetime.utcnow().isoformat()+"Z"
    base={"kind":kind,"actor":actor,"timestamp":now,"payload":payload}
    base["record_hash"]=event_hash(base)
    return base
