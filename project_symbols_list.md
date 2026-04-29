---
name: Symbols List — 4BotsBybit
description: Production symbols.json state, tier structure, and full Bybit USDT-perp universe archive
type: project
originSessionId: 5eb329a9-fa6d-4ab4-9f21-be7e401708fa
---
## Current production list (config/symbols.json)

- **80 symbols** as of 2026-04-29 (narrowed from 197 to align with active GA runs).
- tier_1_top: 20 (top by liquidity from cached binance klines, alphabetical)
- tier_2_mid: 30 (random sample from prior tier_2)
- tier_3_rest: 30 (mixed from cache, not in old tiers — broad coverage probe)

**Why narrowed:** GA optimizer was running on top-20 by kline cache size only, while bot traded 197 — params didn't generalize. The 80-symbol set is what a single GA run can realistically cover, with structured diversity for "what works where" analysis. Backup of prior 197 list at `config/symbols.json.bak_20260429-153147`.

**Manual blacklist (active 168h from 2026-04-29):**
RAVEUSDT, POLUSDT, BSBUSDT, XLMUSDT, SOONUSDT, KATUSDT — 30d real losses (auto-cleanup).
Stored in `symbol_blacklist` table; check `is_symbol_blacklisted(sym)` filters them at signal-process time.

## Full Bybit universe archive (config/bybit_usdt_perp_universe.json)

- **539 symbols** — every live USDT-perp on Bybit as of 2026-04-10.
- Saved for future experiments / backfills.
- Contains per-symbol 24h turnover and last_price at snapshot time.
- Regenerate via: `GET https://api.bybit.com/v5/market/tickers?category=linear`.

## Symbols Artem dropped as invalid (bot will reject if reintroduced)

A2ZUSDT, AINUSDT, ALUUSDT, AVLUSDT, COOKUSDT, CTSIUSDT, DGBUSDT,
DODOUSDT, HOOKUSDT, IDEXUSDT, L3USDT, NFPUSDT, NSUSDT, NTRNUSDT,
OBTUSDT, ONEUSDT, PONKEUSDT, SDUSDT, SFPUSDT, SKYAIUSDT

These either never existed, got delisted, or are spot-only (not perp).

**How to apply:** If asked to add/remove symbols, update config/symbols.json and restart SignalBot. If doing portfolio-level backtesting or coverage analysis, pull from config/bybit_usdt_perp_universe.json — it's the complete catalog.
