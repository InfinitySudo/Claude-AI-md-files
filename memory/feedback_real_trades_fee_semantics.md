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
