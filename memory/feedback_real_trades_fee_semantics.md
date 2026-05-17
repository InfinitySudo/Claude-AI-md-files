---
name: real-trades-fee-semantics
description: "В real_trades.realized_pnl_usd хранится УЖЕ NET (Bybit closedPnl); в simulated_trades — GROSS. Любой агрегатор, считающий net = realized − fees, на real-таблицах двойной счёт фи."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c9644492-6498-4771-8705-09a9325b061e
---

Асимметрия колонки `realized_pnl_usd` между двумя trade-таблицами:

- **`real_trades.realized_pnl_usd`** — пишется в `order_executor_wrapper_v3.py:156, 209` как `net_pnl = sum(closedPnl for chunks)`. Bybit `closedPnl` **уже net of openFee+closeFee**. `fees_paid_usd` отдельно хранится как `openFee + closeFee` для отображения, но **не должен снова вычитаться**.
- **`simulated_trades.realized_pnl_usd`** — пишется в `paper_trading_simulator_v3.py:464` как сумма partial price-move PnL **без** комиссии. `fees_paid_usd` отдельно. Здесь `net = realized − fees` корректно.

**Why:** До 2026-05-16 `statistics_manager_v3.py` применял единую формулу `NET = realized − fees` ко всем таблицам. На real-таблицах это давало двойное вычитание fees и расходилось с фактическим PnL примерно на величину fees (для CONS на 16 мая: dashboard $0.66 при реальной БД $13.29, fees $12.44).

**How to apply:**
- Используй helper `StatisticsManager._is_real_table(table)` и `_net_pnl_sql(table)` (добавлены 2026-05-16) — они возвращают правильное выражение для NET в зависимости от таблицы.
- При добавлении новых агрегаторов в `statistics_manager_v3.py` или `dashboard_api_v3.py`: если делаешь `net = gross − fees` в Python — оберни через `if self._is_real_table(table)`.
- При написании скриптов/отчётов, читающих `real_trades` напрямую — НЕ вычитай `fees_paid_usd` из `realized_pnl_usd`. Это сразу даёт fee×2.
- Если перепишут wrapper и `realized_pnl_usd` в `real_trades` станет gross — обнови helper. Не оставляй асимметрию незадокументированной.

Связано: [[project-realized-pnl-column]] (общее описание колонки), [[feedback-real-trades-truth]] (orphans + dup chunks — про другой класс ошибок, не путать).

## 2026-05-17 — Grafana bots4bybit-live dashboard had the same bug

Sub-bug: Grafana dashboard `bots4bybit-live` (resource в `/var/lib/grafana/grafana.db`) имел 5 panels с `(SUM(realized_pnl_usd) - SUM(fees_paid_usd))` для **real**. Из-за двойного вычета "Total PnL real" показывал −$13.11 при реальной DB-сумме +$2.73 (Δ = fees $15.84).

**Где Grafana queries:**
```sql
SELECT value FROM resource WHERE name='bots4bybit-live' AND resource='dashboards';
```
Это JSON dashboard spec. Patch pattern для real-only panels:
```python
old: "(SUM(COALESCE(realized_pnl_usd, gross_pnl_usd, 0)) - SUM(COALESCE(fees_paid_usd, 0)))"
new: "SUM(COALESCE(realized_pnl_usd, gross_pnl_usd - fees_paid_usd, 0))"

old: "(COALESCE(realized_pnl_usd, gross_pnl_usd, 0) - COALESCE(fees_paid_usd, 0))"
new: "COALESCE(realized_pnl_usd, gross_pnl_usd - fees_paid_usd, 0)"
```
Применять ТОЛЬКО к panels где `FROM real_trades` (НЕ `simulated_trades`). После UPDATE `resource_version=resource_version+1` и `systemctl restart grafana-server`.

Заплачено: 5 panels fixed 2026-05-17 (Total PnL real, Win Rate real, Cumulative PnL real, Top 10 symbols, Recent real trades).

**Правило для будущих Grafana-панелей:** при добавлении любого panel читающего `real_trades` — НЕ писать `realized - fees`. Использовать `COALESCE(realized_pnl_usd, gross_pnl_usd - fees_paid_usd, 0)`. Для `simulated_trades` — старая формула корректна.

## 2026-05-17 — третий случай: hour-heatmap endpoint

`/api/v2/charts/hour-heatmap` (dashboard_api_v3.py:5419) имел тот же bug — `realized - fees` для real → heatmap все cells real-режима казались красными.

Fix: использовать `stats_mgr._net_pnl_sql(table)` helper, а не писать SQL inline. Commit `5185cb8`. Pattern:

```python
net_sql = stats_mgr._net_pnl_sql(table)  # asymmetry-aware
rows = stats_mgr._query(f"""
    SELECT COUNT(*) FILTER (WHERE {net_sql} > 0) AS wins,
           SUM({net_sql}) AS pnl ...
""")
```

**Это уже ТРЕТЬЕ место** где fee-double-count проявился (statistics_manager_v3.py исправлен 2026-05-16, Grafana resource — 2026-05-17, heatmap endpoint — 2026-05-17). Все из-за inline SQL вместо `_net_pnl_sql` helper.

**Universal rule:** любая агрегация по PnL в SQL → **обязательно** через `_net_pnl_sql(table)`. Если helper-import невозможен (Grafana, внешние скрипты) — копируй expression вручную с явным указанием table-shape.

## 2026-05-17 — финальный sweep (8 коммитов)

Полный inventory fix'ов сегодня:

| # | Где | Файл | Commit |
|---|---|---|---|
| 1 | Grafana bots4bybit-live | resource в /var/lib/grafana/grafana.db | manual |
| 2 | /api/v2/charts/hour-heatmap | dashboard_api_v3.py:5419 | 5185cb8 |
| 3 | /api/tp1-investigation + /api/hourly-heatmap (v1) | dashboard_api_v3.py:2700,2780 | d1ddfaa |
| 4 | /api/divergence ._split_stats | dashboard_api_v3.py:3446 | d1ddfaa |
| 5 | /api/scorecard wr_100 + sharpe + maxdd + weekly | dashboard_api_v3.py:3542,3573,3613,3768 | d1ddfaa |
| 6 | main_bot weekly DD guard | main_bot_v3.py:490 | 0b60125 |
| 7 | control_bot stats (WR/wins) | control_bot_stats_extended.py:155 | 0b60125 |
| 8 | hourly_reporter pool summary | hourly_reporter.py:345 | 0b60125 |
| 9 | hourly_reporter wins_money | hourly_reporter.py:480 | 34ccec6 |
| 10 | /api/v2/gerchik/comparison.stream_c | dashboard_api_v3.py:5600 | 97d3306 |

**Что НЕ трогать (paper-only, NET=gross-fees правильно):**
- `database_v3.py:914-918` (FROM simulated_trades)
- `ml_meta_labeler.py:143` (FROM simulated_trades)
- `control_bot_stats_extended.py paper-branch` после моего fix
- meta_labeler join on `st.realized_pnl_usd` (joins simulated_trades)

**Business impact (sub1 main TradingBot):**
- Grafana headline: −$13.11 → +$2.73
- Stream C compare panel: −$13.18 → +$2.70
- Risk Officer verdict: STOP → CAUTION (MaxDD 7.64% inflated → 4.00% honest)
- Weekly DD guard в main_bot: больше не false-trip

Ничего не потеряли, всё было accounting illusion. Реальные деньги на Bybit (+$15.79 за 30d за исключением ghost trades) сходятся с DB +$2.73 + ghost-trades-on-sub3 (-$8.01) + dup-attribution residual.

**Grep-чек для будущего PR:**
```bash
grep -rE "realized_pnl_usd.*-.*fees_paid_usd|fees_paid_usd.*-.*realized" src \
  | grep -vE "simulated|_net_pnl_sql|test_|FROM simulated_trades|paper-branch"
```
Должен быть пустой — иначе новое место с double-fee bug.
