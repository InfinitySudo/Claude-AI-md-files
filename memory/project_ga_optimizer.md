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

---

## GPU percent-mode на PK1 — РАБОТАЕТ (2026-05-31, commit e915bca)
`scripts/gpu/`: ga_optimizer_gpu.py GENES=25 (AGGR = a_tp1_percent + 2 BE), CUDA-кернел tp_mode + tp_price_abs precompute, pack_spec len 2*MAX_TPS+4 (tp_pcts vs tp_ratios по spec['tp_mode']). Smoke pop8/gen2 PID 5008 чистый: 0 Traceback/KeyError/NameError, results c **a_tp1_percent** (НЕ a_tp1_ratio), 22s. Полный pop40/gen30 PID 20116 (/tmp/full_pid.txt) идёт, 262 символа, gen0 max=-41.5. НЕ применять в боевые bot_settings без явного OK Артёма.
Деплой: scp 3 файла → tkach@100.99.211.123:C:/Users/tkach/ga_gpu/, md5-verify MATCH, rm __pycache__. Запуск: run_ga.ps1 -Pop -Gens -Seed; живой PID в ga_run.current; results → ga_gpu_results.json.

**⚠️ МЕТА-УРОК (важнее любого кода):** Edit в большом ПАРАЛЛЕЛЬНОМ батче, где хоть один вызов потом Cancelled, молча НЕ применяется ИЛИ применяется частично («file modified since read»). За сессию это случилось 4× — я коммитил недоприменённый pack_spec/GENES и ложно рапортовал «passed»; PK1 падал `KeyError: 'tp_ratios'`. **ПРАВИЛО: критичные правки делать НЕ в больших батчах; после каждой — отдельный grep/exec-verify; коммитить только после pytest + smoke. Не верить "Edit success"/"N passed" из батча, где были Cancelled.** Связано: [[feedback-one-tweak-at-a-time]].
