---
name: project-trader-model-10
description: "10-трейдерная модель (5 paper A–E + real-двойники), opt-in авто-промоутер, и КАКОЙ файл — живой дашборд"
metadata: 
  node_type: memory
  type: project
  originSessionId: b806f64b-ced8-4366-8bd4-6a976968cec8
---

Модель «10 трейдеров» в 4BotsBybit-Trading (Этап 1+2 задеплоен 2026-06-04, commits 97411ab→477610e на master).

**Beacon (2026-06-05, commits da44454):** +Trader 0 (paper-only зонд: 1 дальний TP R20, BE off →
пишет полный MFE peak_pnl_pct) и +Trader F (paper-only адаптив: 1 TP, авто-подстройка). Флаг
`paper_only` в реестре → НИКОГДА не real (гард в trader_promotion + wrapper._effective_mode).
`src/beacon.py` считает expectancy-sweep по сетке 1-10% от MFE Trader 0 (E=hit·(X−fee)−(1−hit)·(SL+fee),
максимум E, НЕ частота закрытий!), X*→R=X*/SL%. `/api/v2/beacon` (кривая) + `/api/v2/beacon/apply` (ручное→Trader F).
Авто-каданс `main_bot._maybe_recalibrate_beacon` opt-in (config `trader_beacon.enabled=false`, как промоутер).
СТАДИЯ 1 (сейчас): зонд копит данные, применяем вручную. СТАДИЯ 2 (позже): включить enabled. UI: секция 🔭 Beacon.

**Реестр:** `src/trader_registry.py` — единственный источник правды. 7 трейдеров:
A=cons, B=trend, C=aggr (хранят legacy config-блоки conservative/trend/aggressive),
D=клон C, E=клон A (блоки trader_d/trader_e), +Trader 0/F (paper_only). У ВСЕХ A–E теперь по 5 TP
(cons-движок tp_count динамический = len tp_ratios). Имя в БД-колонке `strategy` = 'Trader A'..'Trader E'/'Trader 0'/'Trader F'
(legacy CONSERVATIVE/TREND/AGGRESSIVE переименованы скриптом `scripts/migrate_traders_phase1.py`,
реверсивно через --rollback). main_bot делает fan-out сигнала на всех 5.

**Режим paper/real:** управляется `trading_mode.trader_real_enabled[trader_id]` (НЕ старый per_strategy).
`order_executor_wrapper._effective_mode` резолвит трейдера через реестр и читает этот флаг (свежее из JSON, TTL 10с).
Все 5 сейчас paper (флаги False). Менять — через dashboard или `/api/v2/traders/<id>/mode` (REAL требует фразу 'I UNDERSTAND REAL MONEY').

**Авто-промоутер:** `src/trader_promotion.py`, вызывается из main_bot `_maybe_run_promotion` каждые
`trader_promotion.check_interval_hours`. OPT-IN: `trader_promotion.enabled=false` по умолчанию (отсутствие блока = выкл) —
real-деньги сами НЕ включатся. Критерий promote (7д окно): net>0/≥50 trades/WR≥55%/PF≥1.3 + лимит max_concurrent_real=3.
Demote если real убыточен (≥15 сделок, net<0). Артём включает enabled когда готов рисковать.

**⚠ ОБНОВЛЕНИЕ 2026-06-05:** промоутер был `enabled=true` и флапал C (promote по paper / demote по real-истории — баг), поднял C в real ночью. **Отключён** (`promo_enabled=false`). Сейчас real = только **F** (`trader_f=true`), C=paper. План dual-real C+F = развести по разным суб-аккаунтам (One-Way конфликт). +SL Qty-invalid фикс. Детали: [[project-session-2026-06-05-real-sl-promoter]], [[feedback-real-sl-qty-step]].

**⚠ ЖИВОЙ ДАШБОРД = `/var/www/dashboard/v2.html`** (НЕ в git!), Артём открывает `http://<host>:8080/v2.html#sec-*`
(basic-auth, кеш 1ч → нужен хард-рефреш после правок). Это unversioned prod — бэкап перед правкой.
Репо-файл `TRADING_DASHBOARD.html` = старый v1, НЕ раздаётся. `/var/www/dashboard/index.html` — другой/старый v2 (May 26).
Карточки трейдеров с promote/demote добавлены в v2.html, секция `#sec-traders` в Settings-панели.
V2 API-эндпоинты должны оставаться обратно совместимыми: v2.html индексирует overview.hybrid_mode/charts.series
по legacy lowercase (conservative/trend/aggressive) — см. helper `_v2_out_key` в dashboard_api. См. [[project-hybrid-mode]].
