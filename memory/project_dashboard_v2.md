---
name: Dashboard V2 (per-strategy)
description: Unified per-strategy dashboard at /v2.html — kills paper/real split confusion; v1 still live until cutover
type: project
originSessionId: adfb2918-d7eb-454d-8326-11f044ee5979
---
С 2026-05-05: новый дашборд для 4BotsBybit. Решает корневую проблему: на старой странице `/` (TRADING_DASHBOARD.html) тайлы стратегий брались из правильных таблиц (CONS=paper, TREND=real), но Open Positions / Recent Trades / Per-Symbol / Performance-by-Strategy / TP-Hit-Rates все читали ТОЛЬКО `simulated_trades`. Отсюда 64-vs-67 на TREND, исчезающие real-позиции, и Per-Symbol breakdown без real-данных.

**Why:** hybrid_mode = per-strategy роутинг, а UI делил по paper/real → концептуальное несоответствие.

**How to apply:**
- Новый UI: `/v2.html` (deployed at `/var/www/dashboard/v2.html`); auth_basic как у `/`
- Source: `/root/4BotsBybit-Trading/index_v2.html` (единственное место где правлю)
- Старый `/` (index.html → TRADING_DASHBOARD.html) и все старые endpoint'ы НЕ ТРОГАНЫ. Откат = просто игнорить /v2.html
- `TRADING_DASHBOARD_REAL.html` и `real.html` — мёртвый код, можно удалять при cutover

**Новые эндпоинты (additive, в `src/dashboard_api_v3.py` ~3563):**
- `GET /api/v2/overview` — balance, hybrid_mode (paper/real/paper_pending_real per стратегия), active_pairs, bot_status
- `GET /api/v2/strategy/<name>?period=24h` — name in {cons|trend|aggr|conservative|trend|aggressive}, single source per strategy, поля: kpis, tp_funnel (TP1..TPn + BE + SL), open_positions, recent_trades, mode, mode_label, mode_badge, tp_levels (читается из `trading_v3_artem.json` strategy_parameters.<key>.tp_ratios)
- `GET /api/v2/per-symbol?period=&mode=&strategy=&sort=&limit=` — combined view с explicit `mode` колонкой; единственное место где смешиваются обе таблицы

**Helpers (тоже новые в том же файле):**
- `STRATEGY_V2`, `_v2_canonical(name)`, `_v2_resolve_source(strategy)` — определяет source+table
- `_v2_tp_levels_count(strategy)` — читает live из trading_v3_artem.json
- `_v2_tp_funnel(strategy, table, p_start, p_end)` — обёртка над `stats_mgr.get_tp_hit_rates`

**Известные ограничения (не баги):**
- TREND-real `pnl` = всегда Bybit closed-pnl total (не period-bounded), потому что Bybit endpoint не принимает фильтр стратегии. Унаследовано от `_block()` в `/api/trader-stats`.
- `tp1_triggered` колонка в `real_trades` редко заполнена — TREND TP-funnel показывает 11/64 а не реальные ~28% wins. Это backfill issue, не dashboard.

**Cutover план (когда Артём подтвердит v2):**
1. `/var/www/dashboard/index.html` → бекап
2. `cp /root/4BotsBybit-Trading/index_v2.html /var/www/dashboard/index.html`
3. (Опционально) удалить `real.html`, `TRADING_DASHBOARD_REAL.html`
4. Старые endpoint'ы оставить — `/api/trader-stats`, `/api/funnel-history`, `/api/symbol-breakdown` — они нужны settings/GA/прочим консьюмерам

**6 top-level вкладок (с 2026-05-05):**
1. 📊 Stats — strategy cards + per-symbol breakdown (исходная v2)
2. 📈 Charts — strategy comparison, equity curve, TP funnel timeline, P&L distribution, hour heatmap, scorecard (Chart.js CDN)
3. 🔧 Control — trading state widget с DD bars + reasons, Pause/Resume, mode switch (PAPER/REAL с phrase modal), services panel, logs viewer, blacklist, danger-zone (update-code + clean-db)
4. 🧬 GA — status + schedule + recommended (train vs test per strategy) + top results table + apply history с rollback
5. 🪙 Symbols — 3-column tier editor с pending-changes batch save + available pool с tier-target toggle
6. ⚙ Settings — все 38 SETTINGS_REGISTRY полей с anchor-навигацией + sticky nav

**Endpoints used (UI):**
- v2-only: `/api/v2/{overview,strategy/<n>,per-symbol,charts/{equity,distribution,hour-heatmap,comparison}}`
- existing: `/api/{settings,settings/<k>,services,services/<svc>/<act>,trading-state{,/pause,/resume},mode/switch,bots/uptime,scorecard,funnel-history,dd/ack-session-start,blacklist,blacklist/<sym>,logs/<svc>,update-code,clean-database,symbols,symbols/update,ga/{status,schedule,results,history,run,apply,rollback}}`
- `/api/trader-stats` НЕ используется — заменён v2 endpoints

**Phrase-gated модалки:**
- `I UNDERSTAND REAL MONEY` — global mode → REAL
- `ACK SESSION START` — DD baseline reset
- `APPLY GA` / `ROLLBACK GA` — GA операции
- `UPDATE` — git pull
- `CLEAN` — DB clean

**Файлы:**
- `/root/4BotsBybit-Trading/src/dashboard_api_v3.py` — v2 endpoints (поиск `V2 ENDPOINTS`)
- `/root/4BotsBybit-Trading/index_v2.html` — UI (~1670 строк, vanilla JS + Chart.js CDN)
- `/var/www/dashboard/v2.html` — deployed copy (~97KB)
