---
name: project-paper-double-count-resolved
description: "Paper-simulator до 2026-05-24 удваивал realized_pnl_usd для TP1(*) close с close_pct=1.0 — _partial_close писал full chunk PnL в _realized, _close_trade пересчитывал и СКЛАДЫВАЛ. Пофикшено commit cf6e594 + backfill 195 rows."
metadata: 
  node_type: memory
  type: project
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

## Что было сломано
`src/paper_trading_simulator_v3.py._partial_close_trade` (line 633) аккумулировал `partial_pnl` в `trade['_realized_pnl_usd']`. При `close_pct=1.0` (текущий live tp_distribution=[1.0,…] всех 3 стратегий) `remaining_qty=0` → вызывался `_close_trade` без обнуления `trade['qty']`. `_close_trade` (line 758-761) пересчитывал `pnl_usd` по полному qty, line 844 складывал: `realized_total = _realized + pnl_usd = 2 × gross`.

**Подтверждено SQL**: 195 trades в `simulated_trades` имели `|realized − 2×gross| < 0.01`:
- 48 AGGRESSIVE TP1(a) (хотя AGGR в hybrid mode идёт в real — это legacy paper rows)
- 47 CONSERVATIVE TP1(c)
- 47 TREND TP1(t)
- 41 CONSERVATIVE TP3(c) (старый cascade `[0.5,0.3,0.2]` до 21 мая)
- 9 BE-after-TP, 3 force_paper_to_real_aggr

## Fix (commit cf6e594, 2026-05-24)
В `_partial_close_trade`:
```python
if all_tp_closed or remaining_qty <= 0:
    trade['qty'] = 0.0          # ← ключ: pnl_usd в _close_trade станет 0
    return self._close_trade(trade_id, exit_price, tp_label)
```
`_close_trade` теперь posчитает `pnl_usd=0`, итог `realized_total = _realized + 0 = truth`.

Tests: `tests/test_paper_double_count.py` (3 regression cases — LONG full close, SHORT full close, gross-vs-realized semantics). Full suite 220 → 223 pass.

## Backfill (script + applied)
`scripts/backfill_paper_double_count.py` — dry-run by default, `--apply` для исполнения. Identifier: `|realized - 2*gross| < 0.01 AND |gross| > 0.0001` (узко, не цепляет SL).

Применён 2026-05-24 11:30 UTC: 195 rows исправлено (`realized := gross`).

## Blast radius до фикса
- dashboard headline P&L (sum realized_pnl_usd)
- funnel TP-N cells (sum по close_reason)
- strategy_switcher fitness/WR
- GA fitness function
- control_bot Telegram daily

Все они показывали **2× реальный paper-PnL** для TP1-trades. После backfill — корректны.

## Семантика sim vs real (важно помнить)
- `simulated_trades.realized_pnl_usd` = **GROSS** (без fees)
- `real_trades.realized_pnl_usd` = **NET** (Bybit closedPnl уже включает fees)
- В sim net = realized − fees_paid_usd

Связано: [[feedback-real-trades-fee-semantics]], [[feedback-funnel-vs-close-reason]].
