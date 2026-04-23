---
name: Dup-symbol rule is per (symbol, mode), not per symbol
description: In hybrid mode paper-CONS and real-TREND on the same symbol can coexist — they're separate books
type: feedback
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
Old rule (pre 2026-04-23): `process_signal` rejected any signal whose
symbol already had ANY open position. Logical when there was one global
mode. Broken in hybrid mode: a long-running paper-CONS position on
BTCUSDT silently rejected every incoming real-TREND signal on
BTCUSDT, because `get_open_positions()` now returns paper+real merged.

The right model:

- Paper position lives only in `simulated_trades`. Exchange has zero
  knowledge of it. Adding a real position on the same symbol does NOT
  collide on the venue side.
- Real position is the only one with actual exchange exposure.
- Each pool is its own book; the "1 position per symbol" rule belongs
  inside one book, not across both.

Implementation in `main_bot_v3.process_signal`:
- Compute `sig_effective_mode = trading_mode.per_strategy[strategy]`
  (fallback global `mode`).
- Filter `open_positions` by `pos['mode'] == sig_effective_mode`
  before counting.
- Legacy position dicts without `mode` default to 'PAPER' (correct —
  pre-hybrid all positions were paper).

**Why:** Lets switcher-driven CONS→TREND transitions immediately fire
fresh real signals on previously-paper symbols, without first
force-closing paper trades (which would corrupt CONS data feeding
the next GA run — see `project_fees_accounting.md` and
`project_hybrid_mode.md`).

**How to apply:** ANY new dup/concurrency rule that examines open
positions in hybrid mode must filter by mode (or explicitly state it
applies across both pools, with reason).
