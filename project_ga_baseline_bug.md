---
name: GA reports baseline trades as near-zero
description: GA optimizer writes baseline TEST trades=0/0/5 but direct walk_forward reproduces 3225 trades on same inputs — numbers in ga_results_latest.json are untrustworthy until root cause found
type: project
originSessionId: 2dc45f42-3141-41fc-86cd-010573880879
---
## Symptom
2026-04-20 GA prod run (ga_results_latest.json) reported:
- BASELINE TEST: cons=0 trades, trend=0 trades, aggr=5 trades (WR 0%, all SL, Sharpe -38.59)
- Top-3 candidates all flagged OVERFIT with 22-trade 100%-WR TRAIN corners

Directly replaying `walk_forward_evaluate(current_baseline(), ...)` in a clean process on the **same 113 symbols, same 2026-03-30→2026-04-19 TEST window, same baseline params** returns:
- cons: 1075 trades, WR 36.5%, mean PnL +0.06%
- trend: 1075 trades, WR 30.1%, mean PnL +0.15%
- aggr: 1075 trades, WR 27.2%, mean PnL +0.19%
- combined: 3225 trades, WR 31.3%

Same code path (`walk_forward_evaluate` → `_run_strategy` → `run_backtest`), same data, 645× fewer trades reported. **The delta on the dashboard ("+0.83%/trade vs baseline") is therefore meaningless — baseline is not actually -0.83%, it's closer to +0.12%.**

## Applied GA #1 live performance
Applied 2026-04-15 12:58 UTC based on GA expected WR 69.7% / Sharpe 71.5 / +2.22%/trade.
Actual 7 days live: 416 trades, **WR 2.4%, PF 0.06, worst trade -59.95%**. Catastrophically bad. Auto-rollback did not fire — DD in dollar terms stayed under 5% because PnL summed to +$116 (rare 53% TPs masked mass losses). Rolled back 2026-04-21 22:18 UTC.

## Unverified hypotheses (pick one per session to falsify)
1. **Shallow copy of STRATEGY_SPECS during hof iteration** — `STRATEGY_SPECS["cons"].copy()` is dict-level only; any inner list mutation persists. Walk-forward runs on every hof member before baseline_wf (scripts/ga_optimizer.py:645) so cumulative drift is possible.
2. **Multiprocessing cache write race** — `Pool(workers=3)` runs evaluate() in parallel; `fetch_klines` writes to `data/klines/<source>_<sym>_<interval>_<start>_<end>.json` without locking. Concurrent writes on cold-cache symbols could leave partials. Baseline runs after pool.close() in main process but reads from potentially-corrupted cache files.
3. **Date drift** — no visible reassignment of train_start/test_end between hof loop and baseline_wf call (line 706), but worth verifying with a print-before-call sanity check.

## What makes it tricky
- Each `_run_strategy` call for cons/trend/aggr runs the **same `check_signal` with identical signal_criteria** — they must produce identical trade counts per symbol. GA reported cons=0 trend=0 aggr=5: this asymmetry alone is enough to know something is broken, not just "no signals fired."
- Per-symbol try/except swallows exceptions — a hidden error on most symbols leaves few trades without any log.

## How to verify a fix
Run `scripts/ga_optimizer.py --pop 8 --gens 2 --workers 3` on ~20 symbols and check that `baseline.test.combined.trades` matches a standalone `walk_forward_evaluate(current_baseline(), ...)` on the same inputs.

**Why:** We cannot trust any GA result, including overfit flags, while baseline numbers are wrong. The overfit guard (MIN_TRADES_REQUIRED=50) happens to have caught the 2026-04-20 run, but if a future run generates legitimate 200+ trades with the reporting bug still present, we could apply a truly bad set.

**How to apply:** Do NOT re-run GA for apply purposes until baseline reproduces correctly. For research exploration, ignore the "Δ vs baseline" line and trust only absolute test-period metrics against a manually-verified baseline.
