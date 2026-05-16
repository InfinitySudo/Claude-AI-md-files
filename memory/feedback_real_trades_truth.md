---
name: Real-mode dashboard — Bybit is the only truth
description: 6 stacking bugs made the BD-derived real PnL diverge from exchange by $8+. Lessons + how Bybit closed-pnl actually works
type: feedback
originSessionId: 5926453b-aa53-449f-9edc-92fc5d971f80
---
When the dashboard's "P&L (Real)" disagrees with the wallet diff,
trust the exchange. real_trades has known data-loss paths.

## Bybit closed-pnl truths (verified 2026-04-25)

- Field name is `closedPnl`, ALREADY net of fees. Old code added a
  fictional `cumExecFee` (doesn't exist on this endpoint).
- Real fees come from `openFee` + `closeFee` (separate fields per
  chunk). Sum them for total fees on the trade.
- One position = N closed-pnl entries when it exited via partial TPs.
  Each TP fire = one entry, sorted by `createdTime`. Old reconciler
  used entries[0] only, dropping every chunk except the final one.
- `qty` on each entry is THAT chunk's qty, not position qty.
- `avgEntryPrice` on each entry is the same across chunks (the
  position's entry).

## Why DB lies

- `insert_real_trade` is best-effort and silently drops some opens —
  exchange has positions for which no DB row exists ("orphan trades").
  Their PnL never lands in `real_trades`.
- Overlapping entry/closed windows on same symbol double-count chunks
  during backfill (RAVEUSDT: 4 DB rows, 11 exchange chunks, ~$2 of
  loss double-attributed).
- close_reason for SL-after-partial-TPs loses the TP1/TP2 attribution
  because real_trades has no tp1_triggered / tp_levels columns.

## Source of truth pattern

For "headline" real metrics (P&L total, fees paid):
  → `get_bybit_realized_pnl()` in dashboard_api_v3.py — sums
    closedPnl + fees across ALL traded symbols since cutover, cached
    2 min.

For per-trade attribution (open list, individual rows, TP funnel):
  → real_trades / real_trades_compat. Live with their gaps.

For uPnL on open positions:
  → `/v5/position/list` overlay (overlay_real_positions). Mark price
    + funding-adjusted, matches Bybit UI.

**Why:** wallet diff ≈ closedPnl sum + open uPnL. If your dashboard
disagrees with that arithmetic by more than $1, your DB is the lying
party.

**How to apply:** any new real-mode aggregate display goes through the
exchange-truth helpers, never raw SUM(realized_pnl_usd) FROM real_trades.

## 2026-05-16 — SL vs FORCE split (close_reason honesty)

`close_reason` теперь имеет отдельный 'FORCE' bucket для закрытий, которые НЕ были настоящим Bybit-SL hit. Логика в `_infer_close_reason` (`order_executor_wrapper_v3.py:660`):
- 'SL' — есть chunk в ±1% от sl_price (настоящий стоп)
- 'FORCE' — pnl≤0 + ни одного SL-chunk (раньше всё шло в 'SL')
- TP/BE/LIQ как раньше

Источники FORCE (по наблюдениям 2026-05-16):
- BE-trail сдвинул Bybit SL на entry±0.5% но не обновил `sl_price` в DB (исправлено: `_maybe_move_be_real` теперь синкает sl_price)
- Manual close, watchdog, signal-reversal, dust-sweep
- Высокий slippage в Bybit-SL fill

`close_source` (VARCHAR(32)) на real_trades говорит ОТКУДА классификация: `bybit_sl`, `bybit_tp`, `bybit_liq`, `inferred_be`, `force_inferred`, `force_inferred_backfill`.

**Consequences для метрик:**
- WR_TP считай как TP / (TP+SL+FORCE) — иначе занижено
- Strategy switcher: FORCE считается как SL (SQL: `LIKE 'SL%%' OR = 'FORCE'`) — поведение свитчера не менялось
- Auto-blacklist (5-streak SL → 48h pause): FORCE НЕ ловится через `startswith('SL')` — только настоящие SL стопают символ
- GA fitness: если используешь real-data, фильтруй FORCE отдельно (overfit на грязных метках был причиной)

**Backfill 2026-05-16:** 46 historic SL rows (60% от 76 total) переразмечены в FORCE. close_source='force_inferred_backfill'.

## 2026-05-16 follow-up — narrowing the DB gap

Reconciler (`order_executor_wrapper_v3.py`, 60s tick) теперь делает две дополнительные вещи каждый tick:

- **Partial-close writeback** (`_writeback_partial_realized`): когда `qty < initial_qty` (TP1/TP2 сработали но позиция ещё открыта), суммирует closed-pnl chunks и пишет в `real_trades.realized_pnl_usd` на open row. До этого realized_pnl был NULL до полного закрытия — отсюда занижение headline на сотни долларов.
- **Funding tracking**: новая таблица `bybit_funding_settlements` (id, settlement_time, symbol, funding_usd, bybit_tx_id UNIQUE). Пуллится из `/v5/account/transaction-log type=SETTLEMENT`. Surfaced в `/api/v2/overview` как `funding_settled_usd` и в header chip "💱 funding ±$X.XX".

Это закрывает большинство расхождений Wallet Δ vs DB realized sum. Остаточное расхождение после фиксов (если есть) — реальные orphans (exchange position без real_trades row) — расследовать через сверку Bybit closed-pnl chunks vs real_trades trade_id.
