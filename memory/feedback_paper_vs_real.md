---
name: Hybrid trading mode (CONS=paper, TREND/AGGR=real)
description: 2026-04-23 the system runs PER-STRATEGY routing — CONS still paper (until GA delivers profitable params), TREND/AGGR live on Bybit mainnet
type: feedback
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
**Updated 2026-04-23**: The system is no longer a simple PAPER/REAL
flag. It's hybrid: per-strategy routing.

## Current state

- `trading_mode.mode = 'PAPER'` (global fallback) but
- `trading_mode.per_strategy = {CONSERVATIVE: PAPER, TREND: REAL,
  AGGRESSIVE: REAL}` overrides per signal.
- `current_strategy = TREND`, `strategy_mode = MANUAL` (set
  2026-04-23) — first TREND signal will fire a REAL Bybit order.
- Bybit wallet **$200.92 USDT** (Артём пополнил с $100.38 →
  $200.92 на 2026-04-23). 0 open positions on exchange.

## Why hybrid

Backfilled fees revealed (14d × 900 trades):
- **TREND**: WR 62.9%, PF 1.94, +$0.67/trade — provably money-maker
- **CONS**: WR 40.2%, PF 0.96, **−$0.016/trade** — fees eat the edge

Single-flag flip would have sent CONS live too. Hybrid keeps CONS
paper while GA hunts for params that flip its sign; TREND/AGGR go
real now because the data already supports it.

## What this means for code work

- **Restarting `bybit-tradingbot`** is now risky for in-flight TREND
  positions on the exchange. Open positions stay (ByBit keeps them),
  but the local monitor restart can miss state for a moment. Restart
  when no real positions are open, or expect a brief reconciliation
  on the next loop iteration.
- **Restarting `dashboard-api`** is safe IF subprocesses are detached
  (start_new_session=True — done 2026-04-22). Otherwise it kills any
  running GA. See `feedback_ga_subprocess_detach.md`.
- **Switcher AUTO mode (currently MANUAL)**: when re-enabled, switcher
  will move CONS↔TREND automatically based on win_rate. CONS→TREND
  means "real money turns on"; TREND→CONS means "real money pauses".
  This is the operator-intended behavior.

## What to verify before any trade-touching change

1. `trading_mode.mode` AND `trading_mode.per_strategy` in
   `config/trading_v3_artem.json`.
2. `current_strategy` row in DB (latest by updated_at) — that
   determines which pool the next signal goes into.
3. `strategy_mode` setting in bot_settings — AUTO vs MANUAL controls
   whether switcher will flip strategies on its own.

**Why:** Conflating "the global mode" with "this strategy's effective
mode" leads to wrong reasoning about where signals flow. See
`project_hybrid_mode.md` for full architecture.
