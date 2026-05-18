---
name: feedback-bybit-tp-limit-quirks
description: Подводные камни Bybit set_trading_stop с tpOrderType=Limit и правильный аудит TP-ордеров через /v5/order/realtime
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d9bdd894-aa1e-49e1-88f4-1516a7268f88
---

При работе с Limit-TP на Bybit (`tpOrderType=Limit` в `/v5/position/trading-stop`) есть 3 ловушки и одна общая ошибка диагностики.

**Why:** 2026-05-17 переключение `tp_order_type=Limit` положило все TP-вызовы на 1.5ч из-за `tpLimitPrice` missing; я провёл аудит через `position.takeProfit` и решил что 17 позиций без TP, хотя для Partial mode это поле всегда 0 (TP стоят как отдельные conditional orders).

**How to apply:**

1. **`tpLimitPrice` обязателен при `tpOrderType=Limit`** — Bybit вернёт `retCode 10001 "tpLimitPrice is required when tpOrderType is limit"`. Фикс в [[project_session_2026_05_17_full]] commit 748ec1a: `bybit_api.py:set_trading_stop` добавляет `tpLimitPrice=takeProfit` (триггер=исполнение) автоматически когда type=Limit.

2. **`tpslMode=Full` не поддерживает Limit** — Bybit: `"tpOrderType only support Market when tpSlMode is Full"`. Для Limit TP всегда `tpslMode=Partial` + `tpSize` с конкретной qty. Full mode = Market only.

3. **TP должен быть ниже MarkPrice для SHORT** (выше для LONG) — иначе `retCode 10001 "PartialTakeProfit:X set for Sell position should be lower than base_price:Y??MarkPrice"`. Если цена ушла за TP, Bybit принципиально не позволит выставить такой TP-Limit. Решение для уже-в-плюсе позиции — market reduceOnly close, а не повторная попытка set_trading_stop.

4. **`position.takeProfit` НЕ показывает Partial TP** — для Partial mode оно всегда `"0"` потому что TP стоят как отдельные conditional reduceOnly Limit orders. Правильный аудит:
   ```python
   r = api._request("GET", "/v5/order/realtime", {"category":"linear","symbol":sym,"limit":"50"})
   tps = [o for o in r['result']['list'] if o.get('stopOrderType') == 'PartialTakeProfit']
   ```
   Каждая позиция должна иметь 3 PartialTakeProfit + 1 StopLoss. Если меньше — TP не выставлен полностью.

Связано: [[feedback_bybit_signing_order]], [[feedback_be_on_real]], [[feedback_real_trades_truth]].
