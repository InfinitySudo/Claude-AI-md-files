---
name: System Baseline V2 — 2026-05-08 rebuild
description: Точка отсчёта новой системы после большого rebuild сессии 2026-05-08; wallet, состав фичей, ключевые проблемы решённые в этой сессии
type: project
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
**Baseline:** 2026-05-08 19:44 UTC, wallet $189.60, equity $189.60, uPnL $0, Bybit 0 open positions. Записано в `bot_settings.system_baseline_v2_at` + `_wallet` + `_note`.

**Why:** За одну сессию задеплоен крупный rebuild — все будущие perf-метрики надо сравнивать ОТ этой точки, не путать с до-rebuild эпохой (старые GA-параметры, broken sharpe-гейт, broken BE offset 3.0%).

**How to apply:**
- Любой analytics-запрос «как бот работает после ребилда»: `WHERE entry_time > '2026-05-08T19:44Z'`
- Все доустановленные фичи (см. ниже) активированы примерно в это окно
- Если деградация после baseline → сравнивать против before_v2 как control

**Что в rebuild вошло (commits master):**
- `2f39188` GA на ПК1 через `/api/ga/run target=pc1`, canonical schema, apply rank #1 cons+trend
- `fb0c724` Sharpe-gate: per-trade-sharpe < 1.0 (N-invariant) вместо broken absolute > 50
- `cb801fe` Meta-labeler V1 (XGBoost) shadow mode, AUC test 0.728
- `108f00f` Risk Officer hourly (deterministic STOP-pause + LLM-on-CAUTION)
- `8a9969e` TIER 1+2: hard cap, daily TG digest 06:30 MDT, auto-blacklist, weekly retrain, MFE/MAE real
- `ee3e75c` TIER 3: TG slash commands, concurrent cap, time filter UI, diagnostics, anomaly + backup
- `bfcd53e` Tune CONS + raise caps (max_open 100, position cap $50, TP 1.5/2.5/4.0, BE offset 3.0→0.1)
- `c584b41` spike_ratio 8.9 → 2.0 (operator decision — widened funnel)

**Active timers по баелайну (10 timer'ов):**
- bybit-risk-officer.timer — hourly
- bybit-claude-watchdog.timer — 4×/day
- bybit-claude-hourly.timer — 2×/day
- bybit-divergence-monitor.timer
- bybit-daily-summary.timer — 06:30 MDT
- bybit-anomaly-detector.timer — 06:00 MDT
- bybit-auto-blacklist.timer — 03:00 MDT
- bybit-db-backup.timer — 02:00 MDT
- bybit-meta-retrain.timer — Sun 04:00 MDT
- bybit-ga-weekly.timer — Sun 17:00

**Текущий operational state на baseline:**
- Hybrid mode: CONS=paper, TREND/AGGR=real (`project_hybrid_mode`)
- Risk Officer: enabled, deterministic STOP-pause on; LLM-on-CAUTION **временно OFF** на 7 дней
- Meta-labeler: shadow mode (log_only=true) — копит data для калибровки
- Concurrent cap: 100, hard position cap: $50/symbol
- CONS: TP 1.5/2.5/4.0, BE 0.5%/0.1%
- spike_ratio 2.0 (relaxed by Артём от 8.9 GA-result)
