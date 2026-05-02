---
name: Fees accounting (paper + real) and historical backfill
description: How fees_paid_usd is computed, persisted, and how the 900-row historical zero was reconstructed
type: project
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
## Fees in the system

- **Entry sizing already accounts for fees**: `risk_manager_v3.py:256`
  computes `qty = risk_usd / (sl_distance + 2 × entry_price × taker)`
  so SL hit = real loss `risk_usd`, not `risk_usd + fees`.
- **PnL columns are GROSS** (no fees): `gross_pnl_usd` and
  `realized_pnl_usd` store price×qty deltas. Fees live in
  `fees_paid_usd` separately.
- **Net = gross − fees** computed in queries via
  `(COALESCE(realized_pnl_usd, gross_pnl_usd) - COALESCE(fees_paid_usd, 0))`.

## Bug that was hiding fees (fixed 2026-04-22)

Two bugs together produced fees_paid_usd=0 on every closed row in
`simulated_trades`:

1. **`database_v3.update_simulated_trade` dropped the key** — it was
   not in the UPDATE column list. Paper_simulator passed `total_fees`
   on close; DB silently ignored it. Default 0 stuck.
2. **`update_simulated_trade_partial` whitelist missing fees_paid_usd**
   — partial closes couldn't persist accumulated fees either.
3. **`insert_simulated_trade` didn't seed opening fee** — open trades
   started at 0 instead of at `qty × entry × taker`.

Fix: all three DB methods now write `fees_paid_usd`. Paper_simulator
now passes cumulative `_fees_paid_usd` on every partial close too
(restart-safe — without this the in-memory tally was lost on bot
restart mid-trade).

## Historical backfill — `scripts/backfill_fees.py`

Reconstructs fees from preserved columns:

```
open_fee     = initial_qty × entry_price × taker
partial_fee_i = tp_i.qty × tp_i.price × taker  (for triggered TPs that
                                                 are NOT the final close)
final_fee    = remaining_qty × exit_price × taker
```

`tp_levels` JSON keeps qty/price/close_pct per TP, so the chunk-level
reconstruction is exact except for the final close (uses exit_price
from the row). Per-trade error well under a fraction of a cent.

Run: `python3 scripts/backfill_fees.py [--dry-run]`. Idempotent — only
touches rows where `fees_paid_usd = 0` AND `status = 'closed'`.

Result on 14d × 900 closed: $43.63 backfilled (avg $0.0485/trade).

## Honest stats truth (post-backfill, 14d)

- Old reported (fees=0): WR 42.2%, gross +$71.84
- Real (with fees):       **WR 41.6%**, **net +$28.20**, fees ate 60.7%
  of gross
- TREND:        WR 62.9%, net +$41.42, PF 1.94, +$0.67/trade ✓
- CONS:         WR 40.2%, net **-$13.22**, PF 0.96, -$0.016/trade ✗
  (the trigger for hybrid mode — see `project_hybrid_mode.md`)

## real_trades schema gotcha

`real_trades` has `fees_paid_usd` column (verified 2026-04-22) but no
`initial_qty` or `tp_levels` — backfill_fees.py only operates on
simulated_trades. real_trades writes fees through the same code path
that fixed simulated_trades; if it ever needs backfill, will need a
different reconstruction (probably from ByBit closed-pnl history).

**Why:** WR/PnL/PF only tell the truth when fees are accounted for.

**How to apply:** ANY new stats query → use
`(realized_pnl_usd - COALESCE(fees_paid_usd, 0))` as the net column,
never raw `realized_pnl_usd`. Bare `realized_pnl_usd` is only for
"gross" displays where the user explicitly wants the pre-fee number.
