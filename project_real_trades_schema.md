---
name: real_trades table schema differs from simulated_trades
description: real_trades is narrower — missing duration_minutes, tp_triggered flags, initial_qty, tp_levels. Aggregates must guard against schema mismatch.
type: project
originSessionId: 02a721df-beff-4bfd-bf57-391bd21672c8
---
`real_trades` and `simulated_trades` are NOT structurally symmetric. When you write a stat function that takes `table` as a parameter and works against both, assume the common subset only.

**Columns in real_trades (2026-04-11):**
id, symbol, direction, entry_price, qty, sl_price, bybit_order_id, bybit_position_id, entry_time, closed_at, exit_price, gross_pnl_usd, pnl_pct (renamed from `gross_pnl_pct` on 2026-04-11 for symmetry), status, close_reason, strategy, created_at, updated_at, fees_paid_usd, realized_pnl_usd.

**Missing vs simulated_trades:** `duration_minutes`, `initial_qty`, `tp_levels`, `tp1..tp5_triggered`, `be_triggered`, `sl_triggered`, `exit_time` (real has `closed_at`).

**How to apply:**
- `statistics_manager_v3.get_alltime_stats('real_trades')` will crash on `duration_minutes` and `pnl_pct` references. Either add the missing columns before invoking it, or guard the call with a `COUNT(*) > 0` pre-check (that's what `dashboard_api_v3.api_trader_stats` does to avoid log spam when `real_trades` is empty in PAPER mode).
- If REAL trading gets wired up later, the executor that writes to `real_trades` must either populate all the simulated_trades columns (backfill the schema first) OR we refactor `get_alltime_stats` to branch on table name. Pick the former — it's less code and keeps `get_tp_hit_rates` working against real trades without duplication.
- Don't "helpfully" drop `gross_pnl_pct`/`pnl_pct` thinking it's dead — `get_alltime_stats` reads it for MAX/MIN profit-pct stats.
