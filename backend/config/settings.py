from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Settings:
    app_name: str = "AEROVA"
    methodology_version: str = "2.0"
    base_period: str = os.getenv("APIX_BASE_PERIOD", "2024-01")
    base_index: float = 100.0
    db_path: str = os.getenv("AEROVA_DB", str(ROOT / "data" / "aerova_live.db"))
    user_agent: str = os.getenv("AEROVA_USER_AGENT", "AEROVA-SIH-Airfare-Research/2.0")
    live_mode: bool = os.getenv("AEROVA_LIVE_MODE", "false").lower() == "true"
    request_timeout_ms: int = int(os.getenv("AEROVA_TIMEOUT_MS", "25000"))
    max_concurrency: int = int(os.getenv("AEROVA_MAX_CONCURRENCY", "3"))

settings = Settings()
