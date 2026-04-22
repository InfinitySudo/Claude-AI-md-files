---
name: Symbols List — 4BotsBybit
description: Production symbols.json state, tier structure, and full Bybit USDT-perp universe archive
type: project
originSessionId: aa3b97ed-792c-4424-94e6-e7fb1991e40f
---
## Current production list (config/symbols.json)

- **197 symbols** as of 2026-04-21 (down from 426 on 2026-04-10).
- tier_1_top: 101 (includes BTC, SOL, DOGE, XRP re-added 2026-04-21 after they'd dropped; ETH/BNB were still present)
- tier_2_mid: 96
- tier_3_rest: 0
- Tiers exist for WebSocket subscription chunking (SignalBot concatenates all three into one subscription).
- Earlier versions: 301 (pre-2026-04-10, no majors), 426 (2026-04-10 rebuild with majors), shrunk to 193 at some point before 2026-04-21 when BTC/SOL/DOGE/XRP fell out.

## Full Bybit universe archive (config/bybit_usdt_perp_universe.json)

- **539 symbols** — every live USDT-perp on Bybit as of 2026-04-10.
- Saved for future experiments / backfills.
- Contains per-symbol 24h turnover and last_price at snapshot time.
- Regenerate via: `GET https://api.bybit.com/v5/market/tickers?category=linear`.

## Symbols Artem dropped as invalid (biba will reject if reintroduced)

A2ZUSDT, AINUSDT, ALUUSDT, AVLUSDT, COOKUSDT, CTSIUSDT, DGBUSDT,
DODOUSDT, HOOKUSDT, IDEXUSDT, L3USDT, NFPUSDT, NSUSDT, NTRNUSDT,
OBTUSDT, ONEUSDT, PONKEUSDT, SDUSDT, SFPUSDT, SKYAIUSDT

These either never existed, got delisted, or are spot-only (not perp).

**Why:** Source of truth for symbol universe — which pairs are traded, how the tier split is organised, and where the full Bybit catalogue snapshot lives for experiments (backtests, portfolio scans, etc.).
**How to apply:** If asked to add/remove symbols, update config/symbols.json and restart SignalBot. If doing portfolio-level backtesting or coverage analysis, pull from config/bybit_usdt_perp_universe.json — it's the complete catalog.
