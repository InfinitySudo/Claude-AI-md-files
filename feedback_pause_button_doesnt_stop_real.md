---
name: feedback_pause_button_doesnt_stop_real
description: "Дашборд \"Pause Trading\" НЕ останавливает real в hybrid-режиме; настоящий рычаг — per_strategy→PAPER"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 06f5640b-7c38-4133-bf29-d3987a435601
---

Кнопка дашборда **Pause Trading** (`POST /api/trading-state/pause`) пишет только `strategy_mode=MANUAL` + `forced_strategy=CONSERVATIVE`. Её допущение «signal_bot эмитит только для current_strategy» **ложно в hybrid-режиме**: маршрут real/paper выбирает `order_executor_wrapper_v3.py` по `per_strategy[<стратегия сигнала>]`, а НЕ по current/forced. Поэтому если `per_strategy.AGGRESSIVE=REAL`, AGGRESSIVE-сигналы продолжают открывать реальные позиции, а дашборд при этом честно красит «PAUSED» (effective_strategy=forced=CONS→PAPER).

Случай 2026-06-01: Артём нажал Pause (23:28 UTC), а AGGRESSIVE открыл ~45 real-сделок после паузы (01:00→17, 02:00→26), 5 позиций висели открытыми. Тот самый слив −$104/нед продолжался.

**Why:** UI-состояние = намерение switcher'а, а не фактическая маршрутизация ордеров. Две разные системы.

**How to apply:** настоящий стоп real по стратегии = `POST /api/per-strategy/<NAME> {"target":"PAPER"}` (PAPER без confirm-фразы, рестартит tradingbot). Глобально — global_mode=PAPER. Открытые real-позиции этим НЕ закрываются (закрывать руками запрещено — только с явного go). См. [[project_hybrid_mode]], [[project_real_global_guard_limitation]]. TODO: чинить сам pause-эндпоинт, чтобы он флипал per_strategy real→paper, а не только форсил CONS.
