---
name: project_pumpdump_selftuning
description: PumpDumpAI self-tuning loop — replay engine + fee-aware BE + learning dashboard; GPU NOT used by design
metadata: 
  node_type: memory
  type: project
  originSessionId: 9b16d2b5-05ef-4976-9e59-f7b97b28c149
---

Self-обучение агента пампов/дампов (2026-06-07, commit 29324f4 в InfinitySudo/PumpDumpAI_Agent; зеркало дашборда Space_Live 7b66673). Расширяет [[project_pumpdump_agent]].

**Решение про железо:** PC1/PC2/GPU и Claude-как-мозг-входа НЕ используются. Это малые данные (сотни сделок, WR ~12%, экспектация на редких 20R-runner'ах) — нейросеть переобучится. Правильный движок = counterfactual replay журнала на CPU (микросекунды).

**Архитектура:**
- `src/replay.py` — replay_trade(trade, params): по MFE (peak_pnl_pct) / MAE (trough_pnl_pct) реконструирует исход при кандидатных TP/BE. Допущения: favourable-first (записанный пик случился до разворота → TP ≤ peak_R заполнялись), неоднозначность ордеринга → пессимизм + флаг uncertain. SL distance держится фиксированной (replay НЕ тюнит SL — нужен ATR, его в журнале нет). fitness = median(R)*0.7 + winrate*0.3.
- `src/levels.py` — общая чистая BE-математика (be_stop_price, be_edge_R), один источник для live tracker и replay.
- **Fee-aware BE** (tracker.py): стоп = entry ± (round_trip_fee% + be_min_profit_pct%), фиксирует чистые +0.4% после комиссий. arm_mode `after_tp1` (дефолт, runner-safe — армится только после банка TP1; это фикс причины, по которой BE был выключен с 2026-05-29: армился на голом пике и срезал runner'ов в ~$0). BE снова ВКЛючён. Ключи в config.tp: be_min_profit_pct/be_cover_fees/be_arm_mode.
- `src/tuner.py` переписан: per-cluster replay-поиск tp_R (±max_step) + глобальный BE-поиск (arm_mode × profit), walk-forward 70/30, **TP1 hard floor ≥ 5R** (min_total_R), бэкап в `_meta.tuning_backup` для rollback, learning-report (event="tuning_run") в журнал. Авто-цикл `_auto_tune_loop` (config.tuner.auto_enabled, auto_interval_hours=24, гейт min_trades_per_cluster=20).
- Дашборд (/var/www/dashboard/pumpdump.html, НЕ в git — бэкап перед правкой): панель «🧠 Learning» + кнопки Tune now / Rollback last + поля BE. Endpoints POST /tune-now, /rollback-tuning (секрет X-PD-Secret, как /settings).

**Реальность на 2026-06-07:** первый /tune-now на живом журнале дал fit_train −0.68 (median R отрицательный) — стратегия в минусе, тюнинг сам по себе это не лечит, узкое место — риск-модель/edge, а не параметры (созвучно [[project_ga_percoin_verdict]]). low_cap гейтнут n=17<20. Всё на PAPER (sub-4).

Тесты: 96→106 pass (1 pre-existing fail test_funding_zero_for_short_trades — не связан). Применять правки по одной и мерить ([[feedback_one_tweak_at_a_time]]).

**Персист позиций + реконсиляция (2026-06-07, commit d44e276):** раньше открытые позиции терялись при каждом рестарте → 98 orphan trade_open без trade_close в журнале. Теперь Tracker пишет `data/open_positions.json` (атомарно, при структурных изменениях; в .gitignore), на старте `_reconcile_open_positions()`: PAPER переусыновляет и тречит дальше по тикам, REAL сверяет с Bybit (`executor.get_open_positions`) через `watchdog_check` (исчезла→RECONCILED_CLOSED, без SL→force-close). `_watchdog_loop` (REAL, 30s) теперь подключён (был определён, но не запускался). Старые 98 orphan'ов НЕ фабриковал закрытиями (это засорило бы replay-тюнер нулями; они инертны — без exit_reason тюнер их игнорит).

**Data-grounded entry signals (commit f78f1e0):** эмпирический разбор Bybit-муверов показал: 24h-движения развиваются 17–39ч (медленные тренды, не минутные вспышки); сырой vol-спайк направленного эджа НЕ несёт (forward 3h: −11%..+27% по монетам — вот причина WR 12%/fit −0.68); mean-reversion надёжен только ПОСЛЕ exhaustion (фейд −15..−39%). `src/signals.py`: exhaustion_reversal (фейд выдохшегося: over-extension+climax-объём+lower-high) и trend_continuation (езда по тренду). `scripts/backtest_signals.py` — валидация по ВСЕЙ вселенной (562 монеты, без survivorship): exhaustion_reversal SHORT +0.78R (n=8, селективный), trend_continuation ~0R (эджа нет). Подключены scan-loop'ом по hot-mover кандидатам, per-signal флаги в config.signals + veto/risk-гарды: exhaustion_reversal ВКЛ (paper, копит выборку), trend_continuation ВЫКЛ. ⚠ существующий WS-детектор (fade-every-spike, vol×5+3%) всё ещё активен и эджа не имеет — кандидат на замену exhaustion-сигналом (будущее решение, по одной правке).

**Дашборд-аналитика + скриншот-workflow (2026-06-07):** на pumpdump-дашборде (только `:8080`-версия, НЕ `:443`/ontime — там `/pumpdump/*` кроме webhook не проксируется) есть встроенный график (TradingView Lightweight Charts, self-hosted `/var/www/dashboard/lightweight-charts.js`): клик по символу в таблицах → свечи+объём+маркеры входов/выходов (source: detector/signal/webhook)+SL/TP, инструменты (fullscreen, гор.линии, линейка, EMA20/50). Эндпоинты агента: `/klines` (прокси Bybit), `/symbol-trades` (из журнала). **Скриншот-канал:** кнопка «📷 скрин области» (html2canvas, self-hosted) → POST `/pumpdump/screenshot` (секрет) → сохраняется в `/root/PumpDumpAI_Agent/data/screenshots/latest.png` (+ shot_<ts>.png, заметка в notes.log). **Артём общается скринами: когда говорит «посмотри скрин» — Read `/root/PumpDumpAI_Agent/data/screenshots/latest.png`** (проверено: image-API рендерит). trade_open теперь несёт поле `source` (detector/signal/tradingview).

**Webhook anti-test-pollution (commit 86181f3):** фантомные BEAT@2.2 LONG в журнале = localhost curl smoke-тест из Claude-сессии (секрет был только в транскриптах, не TradingView/не Артём); каждый прогон открывал paper-позицию, мгновенно «выигрывавшую» TP (live BEAT ~3.0 >> 2.2). Гарды в `_on_webhook`: payload `{dry_run|test:true}` валидирует без открытия; reject если цена отклоняется > `execution.webhook_max_price_drift_pct` (8%) от live mark. 2 фантома вычищены из журнала (бэкап).
