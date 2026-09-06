# AEROVA — India Airfare Price Intelligence Platform

AEROVA is an experimental, auditable airfare-intelligence prototype for the SIH problem statement on a real-time Airfare Price Index for India.

## Current data status

**SYNTHETIC_DEMO** by default. The repository contains a deterministic research dataset for interface and analytics testing. It is not an official DGCA or CPI dataset and must not be represented as such.

## Local run

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
python -m pytest -q
uvicorn main:app --host 127.0.0.1 --port 8000
```

### Frontend
```powershell
cd frontend
npm ci
npm run build
npm run dev
```

Open `http://localhost:3000`.

## Main screens

- `/search` — consumer fare comparison with DEMO/LIVE labels
- `/dashboard` — government-oriented monitoring and APIx analytics
- `/backtest` — verified external benchmark validation
- `/methodology` — statistical and governance methodology
- `/api-status` — 11-source registry and collection audit log

## SIH source registry

All 11 scoped sources are represented. Only permitted/public adapters are enabled by default; others are marked `ADAPTER_PENDING` or `AUTHORIZED_FEED_REQUIRED` rather than being falsely shown as live.

## Publication boundary

Before any policy-grade release, replace the pilot route-weight configuration with a verified DGCA traffic export, connect permitted/authorized date-specific fare feeds, and supply a verified DGCA TMU benchmark for external validation.
