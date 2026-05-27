---
name: GA Prewarm IP-Ban Handling
description: Binance returns HTTP 418 (not 429) under sustained load; prewarm now retries with Retry-After + aborts GA if >10% symbols fail
type: feedback
originSessionId: 1cc97980-661a-4cdd-a4b0-dfefe4d3f4d4
---
GA prewarm against Binance can hit HTTP 418 ("I'm a teapot") — Binance's
*temporary IP-ban* response after sustained 429s. It is NOT a permanent 4xx,
but the original `_http_get_with_retry` treated it as permanent and bubbled
out without retrying.

**Why:** 2026-04-29 GA run got 418 on 73/80 symbols during prewarm, then
ran 12 hours on a near-empty cache and produced overfit garbage (CONS train
$3758 → test $991, AGGR sign-flip). Re-running an hour later worked fine —
the ban was transient.

**How to apply:**
- `src/backtest.py::_http_get_with_retry` — 418 in `_TRANSIENT_STATUSES`,
  honors `Retry-After` header, capped per-attempt sleep.
- `scripts/ga_optimizer.py::_prewarm_cache` — `_PREWARM_FAIL_ABORT_PCT=0.10`;
  if > threshold either 5m (binance) or D (bybit) fails, raises SystemExit(2).
- `src/dashboard_api_v3.py::api_ga_status` — exposes `state='failed'` plus
  `exit_code` and `log_tail` when the transient unit dies non-zero, so a
  prewarm bail surfaces in the UI without SSH.
- Bybit fallback for 5m was considered and rejected: Bybit klines lack
  `buyVolume`, which would change `bs_ratio` semantics and decouple
  backtest from live SignalBot.
- If 418 abort fires, wait ~30 min for ban window and retry. Don't
  force-bypass — the half-empty cache produces meaningless GA params.
