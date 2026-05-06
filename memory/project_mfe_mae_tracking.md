---
name: MFE/MAE excursion tracking
description: peak_pnl_pct/trough_pnl_pct columns on simulated_trades+real_trades; paper updates per WS tick, real columns NULL until v2
type: project
originSessionId: caeefaeb-72c6-46d0-859e-af583c161299
---
## Что есть с 2026-05-06

`simulated_trades` и `real_trades` имеют 4 колонки:
- `peak_pnl_pct` (DOUBLE PRECISION) — MFE = пиковый unrealised pnl_pct за всю жизнь сделки
- `peak_time` (TIMESTAMP) — момент пика
- `trough_pnl_pct` (DOUBLE PRECISION) — MAE = худшая просадка
- `trough_time` (TIMESTAMP) — момент дна

Миграция: `scripts/migrate_add_mfe_mae.sql`.

## Кто пишет

**Paper (CONSERVATIVE):** `paper_trading_simulator_v3.update_trade_price()` обновляет `trade['_peak_pnl_pct']`/`_trough_pnl_pct` на каждом WS-тике. Persist через `_partial_close_trade` (не сбрасывает peak/trough между TP) и `_close_trade`.

**Real (TREND/AGGR):** колонки добавлены в схему, но per-tick хук НЕ повешен — Bybit держит SL/TP server-side, общего in-memory price-loop для open real positions нет. Real-стороне MFE/MAE = NULL до v2.

## Известные ограничения v1

- **Restart-safety:** in-memory `_peak_pnl_pct`/`_trough_pnl_pct` сбрасываются при рестарте бота (тот же класс что `_realized_pnl_usd`). Финальные значения у уже-закрытых сделок корректны; mid-trade рестарт теряет excursion data.
- **Backfill:** 1402 исторических CONS-сделок остались с NULL — невозможно реконструировать без тиковой истории.
- **Real-side:** TREND/AGGR сделки не получают peak/trough вообще.

## Запросы для анализа

SL дотянули до TP1 (+1.6%)?
```sql
SELECT
  COUNT(*) FILTER (WHERE peak_pnl_pct >= 1.6) AS reached_tp1,
  COUNT(*) FILTER (WHERE peak_pnl_pct >= 1.4 AND peak_pnl_pct < 1.6) AS near_tp1,
  COUNT(*) FILTER (WHERE peak_pnl_pct < 0.5)  AS never_in_profit,
  COUNT(*) AS total
FROM simulated_trades
WHERE close_reason='SL' AND status='closed'
  AND peak_pnl_pct IS NOT NULL;
```

BE — насколько выше TP1 уходила цена?
```sql
SELECT
  COUNT(*) FILTER (WHERE peak_pnl_pct >= 2.5) AS over_tp2_zone,
  COUNT(*) FILTER (WHERE peak_pnl_pct >= 2.0 AND peak_pnl_pct < 2.5) AS p_2_to_2_5,
  COUNT(*) AS total
FROM simulated_trades
WHERE close_reason='BE' AND status='closed'
  AND peak_pnl_pct IS NOT NULL;
```

## How to apply

Когда Артём спрашивает про excursion / "до куда дошла цена" / "дотянули до TP" — использовать эти колонки. Если нужен dashboard-виджет (гистограмма SL/BE peak), это follow-up: ждём накопления данных ≥1 неделя, потом добавляем в TRADING_DASHBOARD.html секцию CONSERVATIVE.

Если Артём попросит то же для real (TREND/AGGR), это уже не однострочник — нужен новый WS-loop поверх open real positions с обновлением MFE/MAE в memory + persist при reconciliation. См. `order_executor_wrapper_v3.py:start_real_reconciler`.
