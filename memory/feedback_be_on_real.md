---
name: BE на real (move SL→entry)
description: На real BE-protection реализован отдельным monitor'ом в reconciler — paper держит свою логику, real использует Bybit set_trading_stop
type: feedback
originSessionId: 5eb329a9-fa6d-4ab4-9f21-be7e401708fa
---
Real-positions имеют SL/TP server-side на Bybit. Раньше "BE" на real ставился `place_order_with_tp_sl` как **статический TP** на entry+offset% — НЕ как paper-style move-SL-to-entry-after-activation. Эффект: 0 BE-срабатываний на 55 real TREND трейдов за 30 дней vs 41/67 на paper.

**Why:** root cause real-убытков. Весь edge paper-системы шёл от BE (41 BE × +$2.22 = +$91 покрывали 26 SL × −$1.71 = −$44).

**How to apply:** Fixed 2026-04-29 в `order_executor_wrapper_v3.py:_maybe_move_be_real()`. Реконсайлер каждые 60s для каждого open real_trades:
1. Читает mark_price + entry_price → считает pnl_pct
2. Берёт `be_activation_pct` + `be_price_offset_pct` из `strategy_parameters.<strat>` живой config
3. Если `pnl_pct >= activation_pct` AND `not be_triggered` → `set_trading_stop(sl_price=entry±offset)` — заменяет исходный ATR-SL на тесный BE-SL
4. Помечает `be_triggered=True` чтобы не ре-стрелять

**НЕ путать:** static-BE-as-TP в `order_executor_v3.py` остался — он закрывает остаток на entry+offset%, что норм safety-net. Новая логика добавляет MOVING-SL поверх. Обе работают параллельно.

**Cooldown:** 60s/symbol через `_be_moved_attempts` dict.

**Detection:** ищи `[BE_MOVE_REAL]` в TradingBotV3 логе.
