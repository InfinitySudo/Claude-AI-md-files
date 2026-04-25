---
name: GA Walk-Forward Validation (TODO)
description: Plan to switch GA fitness from full-window to train/test split — proper fix for trade-count overfit corners
type: project
originSessionId: 5926453b-aa53-449f-9edc-92fc5d971f80
---
Quick patches in commit 7e7d5e7 (2026-04-25) cap obvious overfit
(trade-count, Sharpe, min spike) but the proper fix is walk-forward.

## Why current GA overfits

Single-window fitness: GA trains on the full 3.3-month window AND
scores on the same window. Anything that fits noise in those exact
93 days wins, even if it would lose on day 94.

The 2026-04-25 run found `spike=2 / atr=0.348` with 83067 trades
@+0.40%/trade — perfect for the trained window, almost certainly
loss-making on out-of-sample data because the narrow stops can't
survive normal market gaps.

## Plan

1. Split data: TRAIN on first 70% of window, TEST on last 30%.
2. GA fitness = `_compute_fitness(test_pnls)`, optionally with a
   small TRAIN component to keep gradients smooth.
3. Reject candidates where `train_fitness - test_fitness > threshold`
   (clear overfit signal).
4. Add k-fold (e.g. 3-fold rolling) for stability if compute allows.

## Acceptance bar

- Top candidate's TEST avg %/trade within ±25% of TRAIN avg %/trade.
- TEST trade count within 50%-200% of TRAIN trade count (no regime
  switch where strategy stops firing).
- TEST Sharpe ≤ 1.3 × TRAIN Sharpe.

## Files to touch

- `scripts/ga_optimizer.py` → `evaluate()`, `_compute_fitness()`,
  add `_split_window()` helper.
- `scripts/ga_baseline_smoke.py` → smoke must pass on both halves.
- Dashboard GA results section — show TRAIN/TEST split per
  candidate so operator sees overfit at a glance.

**Why:** auto-weekly GA applies the top candidate. If overfit ones
slip through quick patches, real money goes in.

**How to apply:** dedicate a session to this before the next major
GA-driven config change. Until then, the quick patches in
ga_optimizer.py keep the corner candidates out.
