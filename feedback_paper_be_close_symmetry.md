---
name: paper-be-close-symmetry
description: paper-симулятор закрывает BE на be_price (symmetry с real); до 2026-05-19 закрывал на current_price (peak) → 4-5× инфляция PnL
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 49ea4545-bbbc-4b86-b277-32955052d57f
---

`paper_trading_simulator_v3.py:_check_be_close` закрывает BE-trade на **be_price = entry × (1 ± be_offset_pct)**, симметрично с real-режимом.

**Why:** До 2026-05-19 paper закрывал BE на `current_price` (mark когда activation сработала, обычно peak). Real же работает так:
- Реконсайлер `_maybe_move_be_real` двигает Bybit SL на be_price.
- Когда цена откатывается и касается этого SL → fill ≈ be_price.
- closedPnl = (be_price - entry) × qty.

То есть на real BE-close даёт **тонкую прибыль** (offset%), а paper давал **полную прибыль до peak'а**. Result: paper PnL 4-5× больше real на тех же signal'ах.

Это объясняло:
- Расхождение paper +$324 vs real −$17 за 10-15 мая (один и тот же engine, тот же universe сигналов, разный PnL).
- Завышенные GA-backtest результаты на paper (Sharpe 47 vs real PF 0.93).
- Когда Артём настраивал fan-out для A/B/C-эксперимента (CONS real + TREND/AGGR paper), TREND-paper показывал +$1.44 на INJUSDT, при real-эквиваленте ~$0.30 — 4.8× inflation.

**How to apply:**
- Закрытие BE в paper-симуляторе ВСЕГДА через `be_level['be_price']`. Fallback на `entry_price` если be_price не задан (safer чем peak).
- Активация detection остаётся через `current_price >= activation_price` (LONG) / `<=` (SHORT) — это правильно (mark-based trigger).
- TP partial-close и SL-close уже корректно используют target prices (tp_price, sl_price). НЕ менять.
- Backfill closed-trades с close_reason='BE': пересчитать exit_price=true_be_price, gross_pnl=(be_price-entry)×qty×sign, realized=partial+gross.

**Test:** `tests/test_paper_trading_simulator.py::test_be_close_uses_be_price_not_current_price` валидирует семантику.

См. [[fanout-architecture-2026-05-18]] (контекст fan-out где обнаружилось), [[real-trades-fee-semantics]] (тоже про paper-vs-real асимметрию), [[ga-under-review]] (GA over-optimism частично из-за этого bug'а).
