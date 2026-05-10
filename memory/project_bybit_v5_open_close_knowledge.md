---
name: Bybit V5 open/close — verified knowledge
description: Подтверждённые правила и подводные камни Bybit V5 для market open/close на linear perp; e2e-тест в gerchik-trading-agent/tests/manual/bybit_e2e_open_close.py
type: project
originSessionId: 7ecab4cc-5fb7-4e8a-9ff9-8754cff466ae
---
Закреплено живой $5.52 XRP сделкой 2026-05-10 (NET −$0.022). Всё ниже verified, не teoreticheskoe.

## Минимумы (linear USDT-perp) — единые для XRPUSDT, BTCUSDT, ETHUSDT, DOGEUSDT, SHIB1000USDT
| Поле | Значение | Откуда |
|---|---|---|
| **minNotionalValue** | $5 | `lotSizeFilter.minNotionalValue` — qty × price ≥ этого |
| qtyStep | per-symbol | `lotSizeFilter.qtyStep` — XRP 0.1, BTC 0.001, ETH 0.01, DOGE 1, SHIB1000 10 |
| tickSize | per-symbol | `priceFilter.tickSize` — XRP 0.0001, BTC 0.10, ETH 0.01 |
| minOrderQty | per-symbol | `lotSizeFilter.minOrderQty` (часто = qtyStep) |
| maxLeverage | 50–100x | `leverageFilter.maxLeverage` |

## Открытие позиции — sequence
```
1. b.get_instrument_info(symbol)   → precision + minNotional
2. price = b.get_ticker_price(symbol)
3. qty_raw = target_notional / price
   qty = round(qty_raw / qtyStep) * qtyStep    (and bump up if qty*price < minNotional)
4. b.set_leverage(symbol, leverage)             → True if retCode 0 OR 110043
5. b.place_market_order(symbol, side, qty_str)  → returns {orderId, orderLinkId}
6. time.sleep(1.5..2.0)                         → Bybit indexer lag
7. pos = b.get_position(symbol)                 → side, size, avgPrice, unrealisedPnl
   ├─ size>0 значит fill прошёл
   └─ avgPrice = реальный entry (slippage от plan-цены)
8. b.set_trading_stop(symbol, tp_price=str, sl_price=str,
                      tp_order_type='Market', sl_order_type='Market')
   → returns {_ok: True} on success (наш wrapper, см. feedback_bybit_empty_result_truthy_trap)
9. (optional) verify pos.takeProfit / pos.stopLoss заполнены
```

## Закрытие позиции
**Market reduceOnly работает напрямую по qty:**
```
b.place_market_order(symbol, opposite_side, qty_str, reduce_only=True)
```
- НЕ нужен `/v5/position/close-position` endpoint
- TP/SL автоматически отменяются при close (Bybit cleanup)
- Через 1-2s closedPnl появится в `/v5/position/closed-pnl`

## Fee + slippage (verified)
- **Taker fee** = 0.055% × notional → $0.003 на $5, $0.022 на $40, $0.11 на $200
- **Round-trip taker** = 0.11% × notional ($0.006 на $5, $0.044 на $40, $0.22 на $200)
- **Market slippage** на USDT-perp ~0.05–0.20% за круг — зависит от spread/volume
- **Минимальная сделка $5** в gerchik-real стоит ~$0.022 (4 базовых пункта от notional). НЕ "конская комиссия" — это normal taker frictions.

## Подводные камни — все проверены
1. **set_trading_stop возвращает retCode=0, result={}** — пустой dict при success.
   `if not res:` интерпретирует как failure → panic close. **Использовать `if res is None`** или возвращать explicit truthy. См. feedback_bybit_empty_result_truthy_trap.
2. **Market order response НЕ содержит avgPrice/fills** — только orderId. Нужен poll `get_position` через 1.5–2s.
3. **set_leverage retCode=110043** ('leverage not modified') — НЕ ошибка. Уже стоит. Считать как OK.
4. **TP/SL price validation** — для LONG: TP > entry > SL; для SHORT: SL > entry > TP. Bybit retCode 110003 при нарушении.
5. **Position mode (Hedge/One-Way)** — мы шлём `positionIdx=0` (One-Way). Если account в Hedge mode → retCode 110013 "position mode mismatch". Defensive: при init вызвать `/v5/position/switch-mode` (но обычно не надо если account настроен).
6. **Margin mode (Isolated/Cross)** — гайки уже на счёте, мы не трогаем. set_leverage применяет к текущему mode.
7. **recvWindow=5000** в нашем коде — стандарт. Если timestamp drift >5s → retCode 10002.

## E2E test
Запуск: `cd /root/gerchik-trading-agent && python -m tests.manual.bybit_e2e_open_close`
Стоит ~$0.022 (2.2 цента). Делает full cycle XRPUSDT $5.50 LONG → TP/SL attach → market close.
Использовать после любых изменений в `bybit_client.py` или `real_executor.py` чтобы убедиться что happy-path не сломали.

## Что в нашем коде УЖЕ правильно
- `set_leverage` обрабатывает 110043
- `place_market_order` шлёт qty как string (Bybit требует), positionIdx default=0
- `_round_to_step` + `_fmt_price` чистят float-артефакты
- После entry sleep(1.5) + verify position size>0
- set_trading_stop возвращает explicit truthy на success (post-fix)

## Что в нашем коде ещё стоит улучшить (не блокеры)
- Validate `minNotional` в `compute_qty` (risk_manager.py) перед place_order — сейчас может проскочить $1 qty, Bybit отбросит retCode 110045
- Validate TP/SL relative to entry перед `set_trading_stop` — pre-emptively, без round-trip к Bybit
- Если `place_market_order` вернул retCode != 0, surface retMsg вверх (сейчас просто None)
