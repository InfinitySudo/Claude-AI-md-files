---
name: paper-be-backfill-2026-05-19
description: 549 paper BE-trades пересчитаны с be_price вместо peak; Grafana panels получили hybrid_baseline filter
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 49ea4545-bbbc-4b86-b277-32955052d57f
---

**2026-05-19** — после починки paper-симулятора (BE-close на be_price, commit 92648bc), backfill всех 549 закрытых paper-BE-trades в `simulated_trades`. Также Grafana `bots4bybit-live` dashboard получил `WHERE entry_time >= '2026-05-18 23:14:12'::timestamp` filter во все 13 SQL panels чтобы UI показывал только пост-fan-out выборку.

**Why:** paper-симулятор закрывал BE на `current_price` (peak), не `be_price`. На исторических 1176 closed paper-trades 549 имели close_reason='BE' и были inflated 3-5× (см. [[paper-be-close-symmetry]]). Headline paper PnL в Grafana был +$564 (inflated), реалистичный — после backfill **±$0**.

**Backfill итог**:
- AGGRESSIVE: 17 closed, 2 BE → net **+$0.13**
- CONSERVATIVE: 1022 closed, 518 BE → net **−$94.69**
- TREND: 151 closed, 29 BE → net **+$35.61**
- **Sum:** ~**−$59** (vs было +$256+ inflated)

Snapshot ДО backfill сохранён в `simulated_trades_pre_be_backfill_20260519` (549 строк) — restore возможно:
```sql
UPDATE simulated_trades st SET
  gross_pnl_usd = b.gross_pnl_usd,
  realized_pnl_usd = b.realized_pnl_usd,
  exit_price = b.exit_price,
  pnl_pct = b.pnl_pct
FROM simulated_trades_pre_be_backfill_20260519 b
WHERE st.trade_id = b.trade_id;
```

**Grafana filter** — hardcoded `2026-05-18 23:14:12` (нельзя SELECT-подставить из bot_settings в Grafana SQL). Если hybrid_baseline_at сдвинется — нужно тоже patch'нуть Grafana SQL'и через [[grafana-v13-resource-table]] паттерн (UPDATE sqlite + bump resource_version + restart grafana-server). Сейчас все 13 panels (`Total PnL real/paper`, `Closed`, `WR`, `Open`, `Cumulative PnL`, `Exit reason distribution`, `Top 10 symbols`, `Recent real trades`) фильтруют по этой дате.

**How to apply:**
- Дальнейшие fixes paper-симулятора могут требовать backfill: schema `simulated_trades.gross/realized` снова станет inconsistent если новая логика close-семантики появится. Используй паттерн snapshot + WITH-based UPDATE.
- НЕ запускать paper-симулятор re-replay (нет engine для этого) — backfill только через SQL recalc на основе уже сохранённых параметров (be_level, tp_levels, qty, direction).

См. [[paper-be-close-symmetry]] (corresponding code fix), [[grafana-v13-resource-table]] (как править Grafana panels), [[real-trades-fee-semantics]] (тоже про paper-vs-real асимметрию, исторический контекст).
