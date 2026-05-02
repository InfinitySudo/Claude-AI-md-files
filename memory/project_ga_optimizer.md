---
name: GA Optimizer for Trading Bot
description: GA parameter optimization system — scripts, dashboard integration, auto-apply workflow, current applied state
type: project
originSessionId: 13ab97bb-8dfe-4655-b013-e399065cc3ba
---
## GA Optimizer — полная система оптимизации параметров

### Что сделано (2026-04-12/13)

**Скрипты:**
- `scripts/ga_optimizer.py` — DEAP-based GA, 27 генов, оптимизирует все 3 стратегии (CONS 3TP + TREND 5TP + AGGRESSIVE 5TP)
- `scripts/ga_notify_on_complete.py` — ждёт завершения GA, отправляет отчёт в TG @DexClaudCodAIBot
- `src/backtest.py` — добавлена стратегия `"aggr"` (5 TP: [5×,10×,15×,20×,30×])

**Dashboard интеграция (Settings → GA Optimization):**
- Кнопка "Run GA Optimization" → запускает в фоне
- "View Results" → топ-3 vs baseline
- "Apply Recommended" → фраза "APPLY GA", сохраняет rollback
- "Rollback" → фраза "ROLLBACK GA"
- Weekly auto-run toggle (Sunday 23:00 UTC) — пока выключен
- **GA Applied — Expected vs Actual**: таблица 1D–7D (каждый день отдельной строкой), заполняется по мере накопления трейдов

**API endpoints:**
- `GET /api/ga/status` — статус прогона
- `POST /api/ga/run` — запуск
- `GET /api/ga/results` — результаты
- `GET /api/ga/log` — лог прогона
- `POST /api/ga/apply` — применить параметры
- `POST /api/ga/rollback` — откатить
- `GET/POST /api/ga/schedule` — weekly toggle
- `GET /api/ga/performance` — actual vs expected (1D–7D windows)

**Файлы данных:**
- `data/ga_results_latest.json` — последние результаты для дашборда
- `data/ga_results_v3_full.json` — output текущего полного прогона
- `data/ga_param_history.json` — история изменений параметров

### Текущее состояние (2026-04-13)
- GA Rank #1 **применён** 2026-04-13 16:21
- Expected: WR 82.7%, Sharpe 20.6, PnL 666.6%, DD 3.9%, Trades 220
- Процесс GA optimizer: PID 731908, running
- Actual данных пока нет (0 трейдов за <1ч)

### Fitness формула
`(Sharpe×0.4 + MeanPnL×10×0.2 + ProfitFactor×0.15 + WinRateBonus×0.10 + TPExitsBonus×0.15) × TradeFactor - DrawdownPenalty`

Веса стратегий: CONS 45% + TREND 35% + AGGRESSIVE 20%

### Рабочий цикл (план)
1. GA прогон раз в неделю (воскресенье)
2. Менять параметры только при Sharpe improvement >30% на TEST period
3. Auto-rollback если drawdown >5% за 24ч после apply
4. Артём подтверждает перед apply

**Why:** Win rate 2.5% на live — нужна оптимизация параметров. GA — первый шаг перед Order Flow.
**How to apply:** Всегда проверять что GA прогон не забился (процесс жив, CPU >0). Результаты приходят в TG автоматически.
