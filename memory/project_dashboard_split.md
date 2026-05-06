---
name: Dashboard split (DEPRECATED)
description: PAPER/REAL split-page setup is dead since 2026-05-05; replaced by per-strategy v2. Memory kept as historical context only
type: project
originSessionId: adfb2918-d7eb-454d-8326-11f044ee5979
---
## ⚠ DEPRECATED — historical only

Split-page setup (`/` → paper, `/real.html` → real) **was dismantled 2026-05-05**:
- `/var/www/dashboard/real.html` — DELETED
- `/root/4BotsBybit-Trading/TRADING_DASHBOARD_REAL.html` — DELETED (was 4725-line dead split-page)

Replaced by **dashboard v2 per-strategy** (see `project_dashboard_v2`),
which dissolved the paper/real binary in favor of explicit per-strategy
hybrid resolution: each strategy tile reads from its own table
(CONS=simulated_trades, TREND=real_trades_compat, AGGR=fallback).

## What's still true from the old split

- `?source=paper|real` query param still works on `/api/trader-stats`,
  `/api/funnel-history`, `/api/symbol-breakdown` — kept for v1 compat.
- `simulated_trades` vs `real_trades`/`real_trades_compat` table choice
  still matters for any new SQL.

## What's NOT true anymore

- `real.html` does not exist
- `TRADING_DASHBOARD_REAL.html` does not exist
- `DASHBOARD_SOURCE` constant only lives on the v1 paper page (and is
  always `'paper'` there now)

For current dashboard architecture see `project_dashboard_v2`.
For "don't break v1 while editing v2" see `feedback_dashboard_v1_v2`.
