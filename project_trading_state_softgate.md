---
name: Trading State Soft-Gate
description: Unified /api/trading-state widget on real.html for "is real on?" — endpoints, semantics, pause/resume mechanics
type: project
originSessionId: 5eb329a9-fa6d-4ab4-9f21-be7e401708fa
---
Soft-gate UX added 2026-04-29. Single source of truth for "is real trading on?" plus one-click pause/resume.

**Endpoints** (in `dashboard_api_v3.py`):
- `GET /api/trading-state` — aggregates strategy_mode + forced_strategy + per_strategy hybrid map + DD guards + scorecard fails. Returns `{state, color, summary, reasons[], strategy_mode, effective_strategy, effective_route, dd, scorecard, actions}`.
- `POST /api/trading-state/pause` — sets `strategy_mode=MANUAL` + `forced_strategy=CONSERVATIVE`. Telegram alert via REPORT bot.
- `POST /api/trading-state/resume` — sets `strategy_mode=AUTO` + writes `current_strategy=TREND` (or first REAL-routed). Real fires immediately, switcher rotates from there.

**State semantics:**
- `effective_strategy = forced_str if MANUAL else current_strategy` — what signal_bot will emit next
- `effective_route = per_strategy[effective_strategy]`
- `LIVE` (green): effective_route=REAL and no DD trip
- `GATED` (orange): DD daily/weekly/total tripped — blocks new real signals via `_check_cumulative_drawdown_guards`
- `PAUSED` (red): effective_route=PAPER. Two sub-cases:
  - `manual_pause`: MANUAL+forced=CONS → user-paused (only this is `can_resume=True`)
  - `auto_paper`: AUTO and switcher chose CONS → resolves itself when WR rotates
- `DISABLED` (gray): nothing in trading_mode routes REAL

**Why:** Артём не понимал, на паузе бот или нет. Scorecard баннер «STOP REAL» — только совет, никаких авто-действий. Теперь есть один индикатор + кнопка.

**Soft-gate trigger:** `scorecard.fail_count >= 3 AND state != PAUSED` → orange "Recommend Pause" button (one-click sets MANUAL+CONS). Telegram one-shot alert when fail_count crosses <3→≥3, tracked via `bot_settings.scorecard_last_fail_count`.

**Widget:** `<div id="trading-state-banner">` in `TRADING_DASHBOARD_REAL.html` (and `/var/www/dashboard/real.html`). Polls every 30s. Paper dashboard doesn't have the widget — paper has no concept of "paused real".

**Constraint trap:** `current_strategy.strategy` has CHECK constraint = ANY(CONS|TREND|AGGR). Cannot write empty/null. Resume MUST pick a real-routed strategy explicitly via `_apply_forced_strategy_side_effects(target)`.

**Action chain:** both pause and resume go through `_write_setting()` which already handles JSON+DB+side-effects+telegram alerts.
