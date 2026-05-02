---
name: GA baseline=0-trades bug — RESOLVED 2026-04-23
description: 2026-04-20 baseline showed 5 trades vs 3225 expected. Root cause found and fixed.
type: project
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
## RESOLVED

Sanity-test (20 majors, live baseline params) on 2026-04-22 showed:
- TRAIN combined: 22881 trades, WR 70.4%, sharpe +112
- TEST combined:   6561 trades, WR 62.5%, sharpe +52
- cons/trend/aggr **symmetric per-strategy trade counts** (7627/7627/
  7627 train, 2187/2187/2187 test) — confirming the old asymmetry
  (0/0/5) was environmental, not a logic bug.

GA prod run #2 with fixes (started 2026-04-22 22:40, PID 2240633) had
pre-run baseline of train.trades=83286 / test.trades=22917 on 194
symbols — proper, non-zero numbers.

## Root cause (multiple compounding issues)

1. **Silent `except Exception: continue`** in
   `_run_strategy` swallowed Binance rate-limit (429) and 4xx errors,
   leaving the per-symbol trade count at zero without any log.
2. **No retry/backoff on fetch_klines** — single 429 burst dropped
   tens of symbols.
3. **No prewarm** — main GA loop hammered the API across all 197
   symbols × 3 strategies × 40 pop × 30 gen, hitting rate limits
   constantly.
4. **Hardcoded baseline()** that didn't reflect live signal_bot_config /
   trading_v3_artem params, so the baseline_wf was measured against
   numbers nobody was actually using live.

## Fixes applied (commit f6557ff and follow-ups)

- `backtest._http_get_with_retry` with exponential backoff on 429/5xx,
  fail-fast on permanent 4xx (e.g. symbol-not-listed).
- `simulate_trade` guards empty `future_klines` (IndexError on edge case).
- `_ERROR_COUNTER` + `_FIRST_ERROR_SAMPLE` replace silent excepts;
  errors surface in `output_data.meta.errors_post_baseline`.
- `copy.deepcopy` for `STRATEGY_SPECS` patch/restore (defensive).
- `_prewarm_cache(symbols, train_start, test_end)` runs serial fetch
  for all symbols × {5m, D} BEFORE the parallel pool starts.
- `_read_live_baseline()` reads spike/bs/volume from
  signal_bot_config.json, atr_multiplier from bot_settings, TP/BE from
  trading_v3_artem.json strategy_parameters (with `/100` for be_pct).
- Pre-run AND post-run baseline_wf with `baseline_divergence` reported
  in meta — drift becomes self-detecting.

Smoke harness: `scripts/ga_baseline_smoke.py` — standalone walk-forward
on 20 majors, no GA loop. Use it to verify any future GA refactor.

**Why kept as project memory:** The diagnosis pattern (silent excepts +
rate-limit + cache divergence) is general; if any other batch process
ever shows "way fewer results than expected", check these three
sources first.

**How to apply:** Don't trust pre-2026-04-23 ga_results_latest.json
files (`mtime <= 2026-04-19 20:57`). All numbers in those are
artifacts of the bug, not real performance.
