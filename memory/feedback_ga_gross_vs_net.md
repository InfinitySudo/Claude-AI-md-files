---
name: feedback_ga_gross_vs_net
description: "GA-панель показывала GROSS PnL как \"net\"; реальный net после издержек уходит в минус — fitness честнее метрик"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d9ff9919-79aa-4ffe-9d6e-8c2ebfb813d9
---

GA-отчёт (`_strategy_metrics` в `scripts/gpu/ga_optimizer_gpu.py`) раньше отдавал
`total_pnl = sum(сырые pnl)` — **GROSS**, а панель карточки трейдера подписывала это
как «test net%». При этом `_compute_fitness` вычитал издержки → панель рисовала
test **+53.8%** при `fitness −60`. Реальный net: gross −0.211%/сделку (а с taker-fee
−0.321%) → у Trader E top200 test было **−63%**, train **−29%**. Эдж тоньше издержек.

**Why:** высокочастотный скальп даёт ~0.10–0.17% gross/сделку, а round-trip издержки
(fee 0.11 + 2×slippage 0.10 + funding 0.011 ≈ 0.32%) съедают его целиком. GROSS-метрика
создаёт иллюзию прибыли. GPU-кернел НЕ вычитал taker-fee (CPU `src/backtest.py:539`
вычитал) → даже fitness был оптимистичен на 0.11%/сделку.

**How to apply:** при оценке любого GA-результата смотри NET (после `COST_PCT_PER_TRADE`)
и `fitness`, НЕ gross. Fix (commit 60df8ee): `_strategy_metrics` вычитает
`COST_PCT_PER_TRADE`, добавлен `gross_pnl` для справки; fitness проброшен в
`/api/ga/trader-result` и показан в карточке. Цель фич-инжиниринга (режим/ликвидации/
agressor-delta) — поднять mean%/сделку ВЫШЕ cost-floor, а не сохранить мнимый gross-плюс.
Связано: [[project_ga_optimizer]], [[feedback_ga_fitness_overfit]], [[feedback_one_tweak_at_a_time]].
