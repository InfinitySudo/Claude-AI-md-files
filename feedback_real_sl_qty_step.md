---
name: feedback_real_sl_qty_step
description: "Conditional maker-SL/entry qty ОБЯЗАН округляться к qty_step символа — иначе Bybit 'Qty invalid' (retCode 10001) и стоп падает на Market-fallback"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ce36190d-1e66-4ff8-83ca-991871de4019
---

В `4BotsBybit-Trading` при `sl_order_type=Limit` (maker-SL через `place_sl_trigger_order` в `bybit_api.py`, conditional reduceOnly Limit /v5/order/create) qty слался СЫРЫМ (`f"{sl_qty:.10f}"` без округления к `qty_step`). Вход (`place_market_order`) флорит qty через `OrderExecutor._normalize_qty`, а SL-conditional — нет. Для монет с целым шагом (HBAR/ENA/ARB/FIL, qtyStep=1) дробный qty `662.04339694` → Bybit `retCode 10001 'Qty invalid'` → стоп падал на Market-fallback (`set_trading_stop` Full). Симптом: `❌ SL conditional FAILED: Qty invalid` ~20×/день у Trader F real (2026-06-05). Позиции были защищены (fallback срабатывал), но терялся maker-fee и надёжность висела на одном fallback.

**Fix (commit `2bf454c`, `src/order_executor_v3.py:set_position_stop_loss`):** перед `place_sl_trigger_order` нормализовать `sl_qty_abs = self._normalize_qty(raw_qty, symbol)` + guard `>= _get_min_qty(symbol)`; ниже минимума → сразу Market-fallback без ошибки. TP-conditional путь (`place_tp_trigger_order`) уже флорил qty (set_position_stop_loss строки ~700-716) — не трогал.

⚠️ Сигнатура helper'а: `_normalize_qty(self, qty, symbol)` (qty ПЕРВЫМ, не symbol). Возвращает int для step≥1.

**Why:** Bybit v5 отвергает любой qty не кратный lotSizeFilter.qtyStep на /v5/order/create; set_trading_stop Full (sl_size=100%) этого не требует, поэтому fallback и спасал.

**How to apply:** любой НОВЫЙ путь, шлющий qty на /v5/order/create (entry PostOnly, SL/TP conditional), ОБЯЗАН прогнать qty через `_normalize_qty` + min-qty guard. Не дублировать форматирование сырого float. Остался не покрытый случай: fallback-TP на полную позицию (`tp_size=position_qty` сырой, set_position_stop_loss ~793) — редкий путь, при желании добить тем же floor. См. [[project-trading-critical-params]] §15 (maker-execution), [[project-trader-model-10]].
