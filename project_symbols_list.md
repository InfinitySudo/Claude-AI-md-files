---
name: Symbols List — 4BotsBybit
description: Production symbols.json state, tier structure, and full Bybit USDT-perp universe archive
type: project
originSessionId: aa3b97ed-792c-4424-94e6-e7fb1991e40f
---
## Current production list (config/symbols.json)

- **426 symbols**, split into 3 tiers by 24h USD turnover (descending).
- tier_1_top: 142 most liquid (BTC, ETH, SOL, XRP, TAO, ZEC, ...)
- tier_2_mid: 142 middle
- tier_3_rest: 142 least liquid
- Tiers exist for WebSocket subscription chunking (SignalBot concatenates all three into one subscription).
- Updated 2026-04-10 after Artem pasted his 421-symbol list — BTC/ETH/SOL were NOT in the previous 301-symbol list (huge missed edge). 20 invalid/delisted symbols dropped from his list, 25 T-Z tail additions (TAO, XRP, ZEC, SUI, WLD, WIF, XMR, TRX, TON, UNI, XLM, etc.) added on top.

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
