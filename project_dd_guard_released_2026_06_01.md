---
name: project_dd_guard_released_2026_06_01
description: "2026-06-01 Артём снял weekly DD-гард (25→40%) + форснул AGGRESSIVE real, хотя AGGR доказанно убыточна — осознанное риск-решение"
metadata: 
  node_type: memory
  type: project
  originSessionId: b67042b8-ce41-4a32-b089-85c0f49c7306
---

**2026-06-01, по явному разрешению Артёма (дважды через AskUserQuestion).** Состояние было PAUSED: weekly DD 25.04% ≥ 25% порог держал все REAL-сигналы (AGGR). Артём выбрал «снять гард сейчас» + «форснуть AGGRESSIVE».

**Что сделано (commit 9ea64af):**
- Жёсткий кламп weekly_max_drawdown_pct расширен 25%→50% в ДВУХ местах: `main_bot_v3.py:732` `_read_setting_pct(... hi=50.0)` И `dashboard_api_v3.py` SETTINGS_REGISTRY `'max': 50.0`. Без обоих настройка не поднималась выше 25 (кламп резал и в API, и в боте).
- Через API выставлено **weekly_max_drawdown_pct=40.0** (POST /api/settings). Total-DD baseline auto-reset → session_start_wallet_usd=$335.41.
- **strategy_mode=MANUAL, forced_strategy=AGGRESSIVE** → state **LIVE, route REAL**. Подтверждено в логах: `Routing: strategy=AGGRESSIVE → effective_mode=REAL` + `💰 REAL ROUTE (AGGRESSIVE)`, real-сделки открываются (риск $1.00/сделку из config).

**Механика weekly DD (важно):** `main_bot_v3.py:738` — это СКОЛЬЗЯЩЕЕ окно 7 дней `SUM(realized_pnl_usd) WHERE closed_at > NOW()-INTERVAL '7 days'`, НЕ календарная неделя и НЕ baseline-кошелёк. Поэтому «новая неделя» сама не сбрасывает — старые убыточные дни выпадают из окна постепенно. Гард = REAL-only (paper не блокирует), блокирует НОВЫЕ позиции всех страт, открытые держит.

**⚠️ КОНТЕКСТ-РИСК:** AGGR spike-momentum доказанно убыточна (EV<0, см. [[project_aggr_no_edge_proven]] — 6 проверок, break-even WR 56% vs факт 48%). Снятие гарда = осознанное решение Артёма пустить убыточный поток, НЕ рекомендация агента. Предохранители остались: weekly 40%, total 30%, daily 35%. Если за 2-3 дня снова в минус — гард поймает на 40%.

**Откат если понадобится:** POST /api/settings/weekly_max_drawdown_pct {value:25}, strategy_mode=AUTO. Связано: [[feedback_session_baseline_transfers]], [[feedback_dd_guard_paper_skip]], [[project_hybrid_mode]], [[feedback_bybit_migration_bypass]].
