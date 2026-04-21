---
name: GA apply must update all three live places
description: Where dashboard's Apply GA writes params — miss any of these and GA has zero effect on the live bot
type: feedback
originSessionId: b448afeb-749e-4f50-8a0d-4509ba083b62
---
GA recommended params have 40 fields but live bot reads them from **three different places**. Apply GA must update all three atomically (fixed in commit 479ea29 on 2026-04-14):

| Param group | Where live bot reads it | Written by api_ga_apply? |
|---|---|---|
| `spike_ratio`, `bs_ratio`, `volume_threshold` | `src/signal_bot_config.json` (`signal_criteria.*`) | yes |
| `atr_multiplier`, `tp1/2/3_percent` (legacy) | `bot_settings` DB table | yes |
| `{c,t,a}_tp*_ratio`, `{c,t,a}_tp*_pct`, `{c,t,a}_be_{activation,offset}` | `config/trading_v3_artem.json.strategy_parameters.{conservative,trend,aggressive}.{tp_ratios,tp_distribution,be_activation_pct,be_price_offset_pct}` | yes (as of 479ea29) |
| Meta: `atr_daily_bars`, `volume_avg_bars`, `trend_bars`, `cooldown_bars` | `config/trading_v3_artem.json.websocket_config.<field>` (signal_bot re-reads via "Reload Config" or next startup) | yes (as of 2026-04-21) — snapshot key is `websocket_config.<field>` |

BE unit scaling: GA params use fractions (`c_be_activation=0.005`), JSON uses percentages (`be_activation_pct=0.5`). `api_ga_apply` multiplies by 100 before writing.

`risk_manager_v3.calculate_{conservative,trend}_tp_be` used to have TP ratios hardcoded in function body; refactored to read from `self.{cons,trend}_config.get('tp_ratios', ...)` with baseline fallbacks (1×/3×/5× SL for CONS, 3/6/10/14/18× SL for TREND). AGGRESSIVE already read from config pre-refactor.

**Why:** Discovered 2026-04-14 that two consecutive GA applies both "succeeded" but live positions kept opening with first-apply ratios because `strategy_parameters` block was dead config — all CONS/TREND ratios baked into the Python. User thought `Apply Rank #1` worked, it did not. Backtest comment (`backtest.py:324`) literally said "dead config" before the fix.

**How to apply:** When touching the GA apply or rollback flow:
- Check all three locations listed above are written/restored.
- Do not rely on `strategy_parameters` being live unless the code path above is intact.
- Meta params (atr_daily_bars etc.) still need refactoring if the user wants them GA-optimizable; flag them explicitly — silent no-op is what caused this bug.
- Bot must be restarted after `trading_v3_artem.json` change — config is loaded once at `main_bot_v3.py:47`, not re-read per signal.
