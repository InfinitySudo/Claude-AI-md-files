---
name: realized_pnl_usd column semantics
description: Why simulated_trades has BOTH gross_pnl_usd AND realized_pnl_usd, and which to use for aggregates
type: project
originSessionId: 02a721df-beff-4bfd-bf57-391bd21672c8
---
`simulated_trades` and `real_trades` have two PnL columns with distinct semantics — don't conflate them.

- **`gross_pnl_usd`** = PnL of the **final chunk only** (the last close: final TP, BE, or SL). This is what `_close_trade` in `paper_trading_simulator_v3.py` writes to DB. Partial TP1/TP2 closures do NOT update this column — they only decrement `qty` and set `tpN_triggered`.
- **`realized_pnl_usd`** = **total realized** PnL for the trade = sum of all partial TP closures + final chunk. Added 2026-04-11 to fix dashboard Net PnL underreporting by ~$15 on the paper account. `_partial_close_trade` accumulates into `trade['_realized_pnl_usd']`, `_close_trade` writes the sum.

**Why both exist:** `get_tp_hit_rates` in statistics_manager_v3 reconstructs per-TP-level partial PnL from `tp_levels` JSON + `entry_price` + `initial_qty` for the "TP hit rates" widget. For BE/SL rows it uses `gross_pnl_usd` as the "final chunk" contribution. Changing `gross_pnl_usd` to hold the total would double-count. So `gross_pnl_usd` remains the final chunk (invariant).

**Why:** Before the split, every aggregate query (`SUM(gross_pnl_usd)`) under-reported total PnL on paper: trades that hit TP1 partially (50% closed at profit) then ran to SL had their TP1 profit invisible — only the SL loss on the remaining 50% was summed. Dashboard's TP-breakdown widget showed one number (correct via reconstruction), while the summary showed a worse number (wrong via SUM of final chunks). Delta was ~$15.90 across 186 historical trades.

**How to apply:**
- Any new aggregate that answers "how much did we make?" uses `SUM(COALESCE(realized_pnl_usd, gross_pnl_usd))`. The COALESCE lets pre-backfill rows still return gross_pnl_usd safely.
- `get_tp_hit_rates` must keep using bare `gross_pnl_usd` for BE/SL — don't "fix" it.
- New simulator code that implements partial closures on a new strategy MUST accumulate into `trade['_realized_pnl_usd']`, otherwise paper PnL totals will silently regress.
- Backfill script: `src/scripts/backfill_realized_pnl.py` — safe to re-run (only touches rows where `realized_pnl_usd IS NULL`).
- `real_trades` also has the column (added for symmetry) but is empty in PAPER mode. If REAL executor is wired up later, it must populate the same way.
