---
name: project-ga-under-review
description: "GA на грани отказа 2026-05-13 — выдаёт нереалистичные TP, тратит время; решение fix-vs-kill pending"
metadata: 
  node_type: memory
  type: project
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

**Статус 2026-05-13:** Артём недоволен GA — после Phase 1-4+2.5 realism overhaul + Walk-Forward + дашборд UI, GA всё ещё выдаёт TP=13-48R, нереалистичный spike_ratio=10.8 и т.п. Считает что GA скорее мешает, чем помогает.

**Why:** Несколько недель работы (см. [[project-ga-realism-overhaul]], [[project-ga-walk-forward-todo]], [[project-baseline-v2-2026-05-08]]) не сделали GA полезным. Backtester игнорирует реальную MFE distribution (макс ~2%), Sharpe-cap защищает fitness но не TP-плейн. Артём предпочёл бы вручную править стратегию по графикам/статистике.

**How to apply:**
- НЕ запускать новые GA-прогоны без явного запроса.
- При работе со стратегией предлагать manual-tuning от MFE/MAE и hourly_report анализа, а НЕ GA.
- Если решено **чинить**: следующие шаги в [[feedback-ga-unrealistic-tps]] (MFE-cap на TP, time-stop в backtester, sanity-check apply).
- Если решено **выпиливать**: отключить cron Sun-night GA, скрыть GA-таб в дашборде, оставить код в репо как research-only.
- Связь: [[project-baseline-v3-2026-05-10]] (после wipe всё перезапущено заново — нет данных подтверждающих edge GA-настроек).
