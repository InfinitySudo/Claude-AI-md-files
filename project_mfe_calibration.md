---
name: project-mfe-calibration
description: 📐 MFE tab в dashboard v2 — data-driven TP-тюнинг из реальной peak_pnl_pct distribution; альтернатива GA mirage-у
metadata: 
  node_type: memory
  type: project
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

Создан 2026-05-13 после того как Артём отверг GA-кандидата с TP в космос (13-48R) при реальном max MFE ~2-5%.

**Что есть:**
- `GET /api/mfe/calibration` — per-strategy: current `tp_ratios`/`tp_distribution`/`be_*`, наблюдённые MFE percentiles (p50/p75/p90/p95/p99/max), median SL distance %, рекомендация = MFE_percentile / median_sl_pct
- `POST /api/mfe/apply` (confirm_phrase `APPLY MFE`) — пишет в `trading_v3_artem.json` `strategy_parameters[strategy]`, snapshot в `ga_param_history.json`, live bots подбирают на следующем сигнале
- UI: tab «📐 MFE» в `index_v2.html` (deployed как `/var/www/dashboard/v2.html`) между Control и GA

**Дефолтные percentiles для рекомендаций:**
- CONS (3 TP): [50, 75, 90]
- TREND/AGGR (5 TP): [40, 55, 70, 85, 95]

**Confidence-гейты:** n>=100 → high, n>=20 → medium, иначе recommendation не показывается.

**Why:** GA backtester нашёл нереалистичные TP, теряя время Артёма ([[feedback-ga-unrealistic-tps]], [[project-ga-under-review]]). MFE Calibration строит TP из реальных закрытых сделок post-baseline-v3, поэтому числа достижимы в проде.

**How to apply:**
- При тюнинге стратегий начинать с этой вкладки, а не с GA.
- Если рекомендация низкоуверенная (insufficient_data) — нужно больше сделок, не лезть руками.
- При важных изменениях стратегии прогонять MFE Calibration ПОСЛЕ apply и смотреть как новые сделки сравниваются с целевыми percentile-уровнями.
- `sl_distance_pct` в `simulated_trades` сейчас всегда 0 (баг ingest) — endpoint считает SL distance из `entry_price`/`sl_price`.
- BE-параметры (`be_activation_pct`, `be_price_offset_pct`) пока MFE Calibration НЕ трогает — следующая итерация может добавить BE-tuning из MAE distribution.
