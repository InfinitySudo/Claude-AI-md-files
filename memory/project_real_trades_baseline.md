---
name: real-trades-baseline
description: План набора REAL сделок и условия переключения анализа/ML с paper на real
metadata: 
  node_type: memory
  type: project
  originSessionId: 52cdecb9-174f-4000-b1f8-e17b8d341e9b
---

С 2026-05-17 решено **продолжать копить real CONS статистику** перед любыми крупными изменениями (ML activation, R-up, Risk Officer activation).

**Текущий setup:**
- `mode = REAL` (config/trading_v3_artem.json), `forced_strategy = CONSERVATIVE`.
- Real CONS = 182 trades за последние 7d, ~25 trades/день.
- Paper параллельно идёт (851 CONS за 7d) — но решения по live-настройкам делаем на real, не на paper.
- Все ML/Risk Officer toggles в shadow или OFF — копят данные без влияния на торговлю.

**Why:** анализ за paper (calibration buckets, per-hour, per-symbol, ML scale backtest) может отличаться от реальной картины на real_trades. Прежде чем включать что-то существенное (ML scale, R×2, Risk Officer auto-pause) нужна **real-trades выборка достаточная для калибровки** — иначе риск регрессии.

**Триггер пересмотра:** real CONS накапливает **≥300-500 closed trades** (~3-4 недели при текущем темпе).

**How to apply:** не предлагать активацию `meta_labeling_enabled`, не предлагать scale-up R, не предлагать поднять Risk Officer Master Enabled — пока triger не достигнут. Все аналитические запросы (если их попросит Артём) после этого порога делать на **real_trades**, не на `simulated_trades`. До порога — paper приемлем для аналитики, но в выводах подчёркивать «это paper, не real edge».

**Связано:** [[hybrid-mode]] (paper/real per_strategy routing), [[real-trades-truth]] (БД real_trades имеет orphans/dup chunks — для headline metrics использовать `get_bybit_realized_pnl()`), [[ga-under-review]] (GA сейчас не запускаем без запроса).
