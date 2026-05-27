---
name: Hybrid trading mode (per-strategy paper/real routing)
description: Per-strategy routing machinery still in code, but as of 2026-05-15 ALL three strategies = REAL (full live mode). Hybrid mechanism kept for future paper-shadowing.
type: project
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---

## Current state 2026-05-15

**FULL REAL** — Артём переключил через ControlBot menu, я доправил `per_strategy` в JSON и закрыл 33 open paper-сделки по mark-price (net +$23.86, `close_reason='MANUAL_MODE_SWITCH_REAL'`). Paper-таблица заморожена, real_trades = чистый старт.

```json
"trading_mode": {
  "mode": "REAL",
  "per_strategy": {"CONSERVATIVE": "REAL", "TREND": "REAL", "AGGRESSIVE": "REAL"}
}
```

Backup pre-switch: `config/trading_v3_artem.json.bak_20260515_080243`.

## История

Activated 2026-04-23 after backfilled fees showed CONS net-loss
(-$13.22 / 838 trades / PF 0.96) while TREND was net-positive
(+$41.42 / 62 trades / PF 1.94). На 2026-05-09 после MFE-калибровки CONS вернули в paper, потом 2026-05-15 — full real.

## Config shape (`config/trading_v3_artem.json`)

```json
"trading_mode": {
  "mode": "REAL",                     // global fallback
  "per_strategy": {                   // overrides per strategy
    "CONSERVATIVE": "REAL",
    "TREND":        "REAL",
    "AGGRESSIVE":   "REAL"
  }
}
```

`per_strategy[strategy]` overrides the global `mode`. Strategies missing
from the map fall back to `mode`.

## Where routing happens

- **`OrderExecutorWrapper._effective_mode(strategy)`** — central lookup.
- **`OrderExecutorWrapper._executor_for(strategy)`** — returns
  paper_simulator or real_executor.
- **`OrderExecutorWrapper.place_order_from_signal(signal)`** — at
  src/order_executor_wrapper_v3.py picks executor by signal['strategy'],
  not by init-time global mode.
- **`get_open_positions()`** — collects from BOTH paper_simulator and
  ByBit API; each trade dict has `mode='PAPER'|'REAL'`.
- **`update_price_and_monitor()`** — ALWAYS monitors paper_simulator
  regardless of global mode; real positions handled by ByBit
  server-side TP/SL.

## Where reads need hybrid awareness

- **`main_bot_v3._check_daily_drawdown_guard`**: picks
  `simulated_trades` vs `real_trades` by per_strategy[current_strategy].
- **`main_bot_v3.process_signal` dup-symbol rule**: filters open
  positions by `pos['mode'] == sig_effective_mode` — paper-CONS on
  BTCUSDT does NOT block real-TREND on BTCUSDT. See
  `feedback_per_mode_dup_rule.md`.
- **`dashboard_api_v3` `/api/trader-stats`/`/api/symbol-breakdown`/
  `/api/funnel-history`**: accept `?source=paper|real` to pick the
  table.

## How current_strategy interacts

- `current_strategy` (DB table `current_strategy`) is set by switcher
  (AUTO mode) or ControlBot (MANUAL).
- When current=TREND → all new signals are TREND → routed to REAL.
- When switcher AUTO flips back to CONS (win_rate drops) → all new
  signals become PAPER again. Real money pauses without operator.
- This is the "market alive → real money, market dead → paper" loop
  the operator wanted.

**Why:** Splits "is market profitable enough" (auto switcher decision)
from "are these specific params live-money-worthy" (per-strategy mode).
GA-validated TREND/AGGR live; not-yet-GA-validated CONS keeps paper.

**How to apply:** When adding any read of trades data, ask "should this
follow per-strategy routing?" — if it's about a specific strategy,
yes; if it's a portfolio-level aggregate, surface BOTH pools labeled.
