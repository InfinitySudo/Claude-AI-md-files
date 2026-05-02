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
