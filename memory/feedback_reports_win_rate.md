---
name: Win Rate = realized_pnl_usd > 0 (money-based, not TP-based)
description: Correct WR for partial-close strategy — count trades that netted positive money across all chunks, not trades where "a TP hit"
type: feedback
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
On 2026-04-22 Artem reviewed the dashboard and called the WR definition
misleading. Background: the bot closes in chunks (CONS = 50/30/20 on
TP1/TP2/TP3). A trade can hit TP1 and then hand back the remaining qty at
SL, ending net-negative but with `close_reason LIKE 'TP%'`. A trade can
also close at BE with a tiny positive residual from the +offset_pct BE
price.

**Canonical definition from now on:**

- **Win**: `realized_pnl_usd > 0` — actual money made across all chunks
- **Loss**: `realized_pnl_usd < 0`
- **Scratch**: `realized_pnl_usd = 0` (rare, basically exact BE with no prior TPs)
- **Win rate**: `wins / closed * 100`

`realized_pnl_usd` (not `gross_pnl_usd`) is the correct column — it
contains the SUM across all close chunks. `gross_pnl_usd` only holds the
final chunk and is unsafe for WR. See `project_realized_pnl_column.md`.

**Why this supersedes the old "close_reason LIKE 'TP%'" rule:**

The old rule overcounted: TP1-then-SL = "win" because a TP label exists,
even though net PnL is negative. That's what Artem saw and objected to.
`realized_pnl_usd > 0` answers the only question that matters: *did the
trade make money*.

**How to apply:**

- Use in ALL stats queries: period, strategy, symbol, alltime, hourly
  reports, control bot `/stats`, dashboard API.
- `close_reason` stays as a SEPARATE "trade outcome" metric: show the
  distribution (TP1-only / TP1+TP2 / TP3 / BE / SL) as a parallel table,
  not folded into WR. It answers "how did the trade close" which is a
  different question than "did I make money".
- Keep showing **Profit Factor** (gross_profit / gross_loss) and
  **avg realized_pnl_usd per closed trade** alongside WR — WR alone hides
  huge wins/tiny losses or vice versa.

**Do NOT** rely on BE-vs-loss classification for WR. A BE trade with
`realized_pnl_usd = +$0.03` is a (tiny) win; with `realized_pnl_usd =
-$1.20` it's a loss. The pnl column decides.
