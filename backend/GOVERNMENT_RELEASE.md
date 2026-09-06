# AEROVA Government Release Checklist

## What is implemented
- Real-source collection layer with airline and OTA adapters.
- `FareObservation` audit schema: source, granularity, timestamp, route, travel date, fare components, availability, lead time, parser version, compliance state and content hash.
- No CAPTCHA/security bypass and fail-closed robots verification.
- Dual data modes: LIVE public collection or clearly labelled SYNTHETIC_DEMO.
- Cleaning: invalid/sold-out/cancelled removal, IQR/MAD outlier screening, quality score.
- APIx weighted route index, T+1/T+7/T+15/T+30/T+45 lead-time analytics, route heatmap, airline/source comparison, anomalies and short forecast.
- Backtest endpoint that accepts a DGCA TMU benchmark CSV and refuses to invent benchmark data.
- Government dashboard with data-mode banner, methodology version and quality/audit views.

## Policy-grade data configuration still required before official publication
1. Replace the pilot route weights in `data/dgca_route_weights.csv` with a verified DGCA traffic export and retain the original source file/hash.
2. Supply an official/authorized date-specific flight-level feed/API or permitted public source for each airline/OTA. The current route-page adapters are explicitly typed as `DATE_LEVEL_ROUTE_SIGNAL` and are not silently promoted to exact flight inventory.
3. Provide a DGCA TMU benchmark export (`date,route_id,avg_fare`) for the requested 30-day validation window.

These are deployment-data/configuration controls, not hidden mock-data fallbacks.
