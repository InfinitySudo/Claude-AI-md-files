---
name: Report metrics must use close_reason, not gross_pnl
description: BE trades leak into pnl-based "wins"; always define win rate as TP-only close_reason across hourly/24h/status reports
type: feedback
originSessionId: aa3b97ed-792c-4424-94e6-e7fb1991e40f
---
Reports and stats queries in this codebase historically used
`gross_pnl_usd > 0` as the "win" criterion. This is subtly wrong:

A BE close is NOT a zero-pnl event in the DB. BE triggers after at
least one TP has partially closed, and `simulated_trades.gross_pnl_usd`
in the current schema holds only the **final chunk's** PnL (the
remaining qty closed at BE). That last chunk is typically slightly
positive because BE is set to entry + 0.5% (CONS) or entry + 1% (TREND).
Result: BE trades with a tiny residual positive pnl get counted as
wins, inflating win rate above the real TP-reaching rate.

Concrete example from 2026-04-10: the "Win Rate: 9.7%" in the 24h
Telegram report was hiding the real fact that **0 out of 64 closed
trades had ever reached TP1**. 19 were BE (neutral), 45 were SL. The
bot was losing money on every cohort and nobody knew.

**Why:** The pnl-based win criterion silently misclassifies BE trades
when the schema keeps only final-chunk PnL.

**How to apply:** When writing or reviewing ANY stats query or report:

- Wins: `COUNT(*) FILTER (WHERE close_reason LIKE 'TP%')`
- BE neutral: `COUNT(*) FILTER (WHERE close_reason = 'BE')` — report separately, don't fold into wins or losses
- Losses: `COUNT(*) FILTER (WHERE close_reason = 'SL')`
- Closed: `COUNT(*) FILTER (WHERE status = 'closed')` — the denominator
- Win rate: `wins / closed * 100`, with a one-line note "TP only, BE = neutral"

Three Telegram reports have been fixed to this rule: `hourly_reporter._generate_and_send_report`, `control_bot_stats_extended.StatsManager.get_stats`, `control_bot_simple_v3.get_stats`. Any NEW report must use the same definition or the two will disagree and one will lie.

Related: when the denominator for TP/SL/BE percentages comes from a
different time window than the numerator, you can get percentages >
100% (happened in hourly report: "SL: 7 trades (175%)"). Use the SAME
window/filter for both. For close-reason counts the natural window is
`status = 'closed' AND updated_at BETWEEN start AND end`.
