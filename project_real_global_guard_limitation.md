---
name: project-real-global-guard-limitation
description: REAL dup-check глобален (любая страта на символе блочит другую) с 2026-05-24 — Bybit One-Way agg. При переходе на multi-strategy-real нужна виртуальная per-strategy книга поверх агрегированной Bybit-позиции.
metadata: 
  node_type: memory
  type: project
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

С 2026-05-24 (commit `631dd30`, файл `src/main_bot_v3.py` + `_count_dup_positions`) в `4BotsBybit-Trading` действует **глобальный** dup-check для REAL: любая открытая real-позиция на символе блокирует новый real-сигнал, независимо от стратегии. Причина — Bybit One-Way физически агрегирует все entries на символ в одну позицию с одним SL; до фикса AGGR-real мог re-entry'ить поверх CONS-real / другого AGGR-real (SUI × 5, DOGE × 4, LINK × 4 на момент фикса).

**Why:** пока в hybrid режим one strategy at a time в real (CONS=paper, TREND=paper, AGGR=real per `trading_mode.per_strategy`) — глобальный guard безопасен, симметрия с paper держится (каждая страта = 1-на-символ в своей книге).

**How to apply:** если Артём решит поднять **2+ стратегии одновременно в real** (например CONS+TREND+AGGR все real), **напомнить ему**: текущий global guard заблокирует более поздние страт-сигналы. Нужна архитектурная задача — «виртуальная per-strategy книга поверх Bybit One-Way»: каждая страта держит свою долю общей Bybit-позиции в DB (qty/entry/SL/TP), reconciler агрегирует на бирже одну real-position; при partial-close распределять fills по strategy-долям. Сигналы переключения mode читаются из dashboard (`/api/settings/per_strategy.*`).

Связано: [[project-hybrid-mode]], [[project-dashboard-apply-chain]], [[feedback-per-mode-dup-rule]].
