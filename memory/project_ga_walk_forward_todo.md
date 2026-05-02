---
name: GA Walk-Forward Validation (ACTIVE)
description: Train/test split inside evaluate() — fitness graded on out-of-sample TEST, with saturating penalty when TRAIN diverges
type: project
originSessionId: 5926453b-aa53-449f-9edc-92fc5d971f80
---
Status: **active** since 91bbd3a → upgraded to 3-fold + ensemble +
apply-gate in 99c855f (both 2026-04-25). Below documents what shipped.

## What ships

`scripts/ga_optimizer.py`:
- `_run_strategy(..., return_with_ts=True)` yields (pnl, ts_ms) tuples.
- 3-fold expanding-window walk-forward inside `evaluate()`.
  Folds: train [0..0.47/0.67/0.87], test [0.47..0.67 / 0.67..0.87 /
  0.87..1.00]. Re-slicing the same `_run_strategy` output → same
  compute as the single-split version.
- Ensemble per fold:
    `0.30 * train_fit + 0.70 * test_fit - K * saturating(train - test)`
  train/test individually clipped to [-100,100] before combining so
  unbounded profit-factor on all-win folds can't dominate.
- Final fitness = mean(fold_scores), clamped to [-100,100].

`src/dashboard_api_v3.py` `/api/ga/apply` overfit gate refuses if:
  - test_n == 0 OR train_avg > 1.5 × test_avg
  - train profitable but test ≤ 0
  - train_n / test_n > 4.67  (test trade rate dropped)
  - max(|sharpe_train|, |sharpe_test|) > 50  (noise-fitting tell)
  - max(dd_train, dd_test) > 100  (>100% loss vs peak)
  - GA's own overfit_warning flag is true
Override with `{"force": true}` in payload.

Synthetic ranking (3-fold + ensemble):
- ROBUST    →  +18.29
- DECENT    →  +16.33
- SPARSE    →  -16.72
- OVERFIT   →  -86.67
- TINY (<50)→ -100.00

## What still uses full-window math

`walk_forward_evaluate(ind, train_start, train_end, test_start, test_end, ...)`
— the dashboard's "show me train/test for this candidate" reporter —
runs `_run_strategy` twice on caller-provided windows. Untouched.
That reporter is what populates `train`/`test` blocks in
`ga_results.json` which the apply-time gate reads.

## Why this matters

Auto-weekly GA applies the top candidate. Without walk-forward, that
top candidate optimizes for a finite past window, not the future. The
2026-04-25 spike=2/Sharpe=194 corner was the canary.

**Why:** real money rides on the post-apply behavior, not the
backtest curve.

**How to apply:** any change to `evaluate()` MUST preserve the
walk-forward semantics. Adding new genes is fine; removing the train/
test split silently is not.
