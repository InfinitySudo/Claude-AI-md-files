---
name: Full REAL trading mode (all strategies live since 2026-05-15)
description: 2026-05-15 — Артём флипнул всё в REAL (CONS+TREND+AGGR). Paper заморожен с снапшотом +$137.98 CONS / +$66.59 TREND. Дальше real.
type: feedback
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
**Updated 2026-05-15**: Полный REAL. 33 open paper закрыты по mark-price (net +$23.86, `close_reason='MANUAL_MODE_SWITCH_REAL'`). real_trades — чистый старт. Hybrid-механизм остался в коде на случай возврата.

## Current state

- `trading_mode.mode = 'REAL'` AND `trading_mode.per_strategy = {CONS:REAL, TREND:REAL, AGGR:REAL}`.
- `simulated_trades` заморожен; новых open paper нет, аналитика бот'а перешла на `real_trades`.
- Pre-switch baseline (paper, 2026-05-15): CONS 996+26 trades +$137.98 / TREND 135+7 trades +$66.59 / AGGR 12 trades +$3.35.
- Backup конфига перед свитчем: `config/trading_v3_artem.json.bak_20260515_080243`.

## Историческое состояние (до 2026-05-15)

- 2026-04-23 → hybrid mode (CONS=paper, TREND/AGGR=real, wallet $200.92).
- 2026-05-09 → откатили TREND/AGGR обратно в paper для GA-тренировки.
- 2026-05-15 → full REAL.

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
