---
name: Dust auto-sweep in reconciler
description: order_executor_wrapper auto-closes <10% qty residuals from server-side TP rounding to prevent orphan dust forever
type: project
originSessionId: 5eb329a9-fa6d-4ab4-9f21-be7e401708fa
---
Bybit's qty step rounding can leave 1–10% of initial qty after all server-side TP triggers fire. Position never reaches 0 → reconciler waits forever (closed-pnl emitted only on full close) → real_trades row stays `status='open'` indefinitely → DB lies about exposure.

**Fix 2026-04-29:** added `_maybe_sweep_dust(row, live_pos)` in `order_executor_wrapper_v3.py`, called from `_reconcile_real_trades_once` for every open row that's still live on Bybit.

**Trigger conditions (ALL must hold):**
- `1 - live_size/initial_qty >= 0.90` (>=90% filled)
- `now - entry_time >= 6h` (mature position)
- 10-minute cooldown per-symbol via `_dust_sweep_attempted` dict

**Action:** reduceOnly Market in opposite direction. Bybit emits closed-pnl entry once size hits 0; next reconciler pass picks up the row via the existing closed-pnl code path and finalizes it normally.

**Constants** (top of class): `DUST_FILL_RATIO=0.90`, `DUST_AGE_HOURS=6.0`, `DUST_SWEEP_COOLDOWN_SEC=600`.

**Origin:** Apr 25 TREND batch (BLUR/SAND/RIVER/BEAT) hit TP1+TP2+TP3 = 100% on paper but rounding left 0.7%–10% dust. Manual cleanup script: `scripts/cleanup_dust_positions.py`.
