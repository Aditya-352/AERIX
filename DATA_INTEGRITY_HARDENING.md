# AEROVA UI + Data-Integrity Hardening

This release separates four operational states: LIVE VERIFIED DATA, SYNTHETIC DEMO, FAILED/BLOCKED COLLECTION, and NO DATA. Synthetic values are never represented as official government observations.

## Source scope
All 11 SIH-scoped sources are registered. Only currently implemented permitted/public adapters are marked `LIVE_PUBLIC_ADAPTER`; other sources are explicitly `ADAPTER_PENDING` or `AUTHORIZED_FEED_REQUIRED`.

## Government release rule
Pilot route weights and synthetic observations are not official DGCA statistics. A verified external benchmark and verified traffic-weight export are required for policy-grade publication.

## Backtesting
The backtest endpoint refuses to fabricate a benchmark. A verified CSV must contain `date,route_id,avg_fare`.
