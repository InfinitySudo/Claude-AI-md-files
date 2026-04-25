---
name: GA Walk-Forward Validation (ACTIVE)
description: Train/test split inside evaluate() — fitness graded on out-of-sample TEST, with saturating penalty when TRAIN diverges
type: project
originSessionId: 5926453b-aa53-449f-9edc-92fc5d971f80
---
Status: **active** since commit 91bbd3a (2026-04-25). Below documents
what shipped + what's still to refine.

## What ships

`scripts/ga_optimizer.py`:
- `TRAIN_FRACTION = 0.70` — first 70% of window = TRAIN, last 30% = TEST.
- `_run_strategy(..., return_with_ts=True)` yields (pnl, ts_ms) tuples
  so the caller can split. Old float-only signature still works for
  the existing `walk_forward_evaluate` reporter.
- `_walk_forward_fitness(pnls_with_ts, ...)` =
    `test_fit - K * saturating(train_fit - test_fit)`
  Saturation around 50 keeps overfit-penalty from dominating ranking
  past where it's decided. Final clamped to [-100, 100].
- `evaluate()` calls `_walk_forward_fitness` per strategy.

Synthetic verification:
- OVERFIT (train +2.3, test -0.5) → -100
- DECENT  (train +2.0, test +1.5) → +14.1
- ROBUST  (train +1.8, test +1.7) → +16.5

## What still uses full-window math

`walk_forward_evaluate(ind, train_start, train_end, test_start, test_end, ...)`
— the dashboard's "show me train/test for this candidate" reporter —
runs `_run_strategy` twice on caller-provided windows and computes
plain stats. Untouched. It's a separate analytical view, not the
fitness path.

## Possible refinements (next pass)

- **3-fold rolling** instead of single 70/30 split. More robust to
  regime accidents on the boundary. Costs 3x evaluate runtime.
- **Acceptance gate at apply-time**: dashboard's "Apply Recommended"
  button refuses if `train_avg / test_avg > 1.5` or
  `train_trades / test_trades > 2.0` for the chosen rank.
- **Weighted ensemble of train and test fitness** (e.g. 0.3*train +
  0.7*test) instead of pure-test, so the GA still gets gradient on
  trades that were predominantly in TRAIN.

## Why this matters

Auto-weekly GA applies the top candidate. Without walk-forward, that
top candidate optimizes for a finite past window, not the future. The
2026-04-25 spike=2/Sharpe=194 corner was the canary.

**Why:** real money rides on the post-apply behavior, not the
backtest curve.

**How to apply:** any change to `evaluate()` MUST preserve the
walk-forward semantics. Adding new genes is fine; removing the train/
test split silently is not.
