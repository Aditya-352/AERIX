# AEROVA Gap 1 — Real Airfare Collection

## What changed

The synthetic engine is no longer the only data-acquisition path. A first-party collector layer has been added under `backend/collectors/`.

### Current live source adapter

- `INDIGO_PUBLIC_ROUTE`
- Uses an official IndiGo public route page.
- Checks `robots.txt` before collection and fails closed if it cannot verify permission.
- Does not bypass CAPTCHA, bot protection, authentication, private APIs, or other access controls.
- Stores observations in SQLite at `backend/data/aerova_live.db`.

### Important limitation

The current public route-page adapter exposes a route-level fare signal, not complete date-specific flight inventory. It therefore must not be presented as a full T+1/T+7/T+15/T+30/T+45 flight-level scraper yet.

The next collector milestone is an authorized/date-specific booking-source adapter with the same canonical interface. Until that exists, AEROVA should label these observations as `ROUTE_LEVEL` rather than pretending they are exact flight quotes.

## Run

From `backend/`:

```bash
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload
```

Then call:

```text
POST /api/v1/collection/collect?source_id=INDIGO_PUBLIC_ROUTE&origin=DEL&destination=BOM&travel_date=2026-09-20
```

Recent stored observations:

```text
GET /api/v1/collection/recent?limit=20
```

Or run the collector directly:

```bash
python -m collectors --origin DEL --destination BOM --date 2026-09-20
```

## Canonical observation model

Every future airline/OTA adapter must emit the same `FareObservation` structure:

- source
- collection timestamp
- origin/destination
- travel date
- airline/flight number
- fare class
- base fare
- taxes
- airport fee
- convenience fee
- total fare
- availability
- lead time
- source URL
- parser version
- collection status/error

This makes it possible to plug in Air India, Air India Express, Akasa Air, SpiceJet and authorized OTA feeds without changing the downstream cleaning/index pipeline.

## Why this is safer

The problem statement asks for anti-bot handling, but AEROVA should not attempt to defeat CAPTCHA or security controls. The collector framework is intentionally fail-closed and source-specific. For restricted sources, the preferred path is an authorized API/feed or a permitted data-access arrangement.
