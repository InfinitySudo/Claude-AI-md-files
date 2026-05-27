---
name: orphan-residual-after-premature-close
description: "Sub-case of [[real-position-bybit-no-db]] — reconciler ставит status='closed' когда Bybit мгновенно показал size=0, но residual возвращается/остаётся. Dust-sweep уже не помогает (бежит только по open_rows). Recovery recipe для re-attach с TP+SL."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ebbb54ec-6bc0-4399-9055-f5381a6995c4
---

**Симптом:** ORPHAN-алерт раз в час на символ, hourly_supervisor шумит, бот не управляет позицией. Внешне выглядит как обычный orphan из [[real-position-bybit-no-db]], но БД говорит `status='closed'` с close_reason='TP1'/'TP4'/'SL' — не пустота.

**Корневой механизм (2026-05-17 FARTCOIN/SOL/BCH):** `order_executor_wrapper_v3._reconcile_real_positions` в строке 124 итерирует `open_rows`. Если `sym not in live_symbols` → fetch closed-pnl chunks и пишет `status='closed'`. После этого dust-sweep (`_maybe_sweep_dust`, строка 139) на этот символ НЕ зайдёт, потому что `open_rows` его уже не содержит. Если residual возвращается на Bybit (Bybit API даёт size=0 в один тик, потом снова >0 из-за округлений / cross-margin перерасчёта / частичного reduceOnly), он становится постоянным orphan-ом.

**Why:** dust-sweep tiers (`(0.99, 0.25h), (0.95, 1h), (0.90, 3h)`) рассчитан на «живой» trade. Premature `status='closed'` обрывает связь DB↔Bybit, и residual висит до ручного вмешательства или SL hit.

**How to apply:**
1. **Не путать с обычным orphan.** Сначала `SELECT * FROM real_trades WHERE symbol=X ORDER BY entry_time DESC LIMIT 5;` — если последняя строка `status='closed'` с близким `qty`/`sl_price` к Bybit-live, это residual-after-close, а не fresh orphan.
2. **Re-attach recipe** (нужно явное разрешение Артёма — это не routine):
   - Получить live данные: `entry=avgPrice`, `qty=size`, `sl=stopLoss` через `ByBitAPI.get_open_positions()` (требует `env -i PATH=/usr/bin python3` — shell имеет `BYBIT_API_KEY=test_key` мусор)
   - Считать TP-уровни: `R = entry − sl` (LONG) или `sl − entry` (SHORT), `TP_i = entry ± R × ratio_i`, ratios из `config/trading_v3_artem.json → strategy_parameters[strategy].tp_ratios`
   - Применить 5 TP отдельными `set_trading_stop(tpslMode='Partial', tp_size=int(qty*pct), tp_order_type='Market', tp_trigger_by='MarkPrice')` с 0.5s паузой; **не дёргать SL** (sl_price=None) если Артём уже выставил руками
   - qty_step+min_qty достать из `/v5/market/instruments-info`; floor TP-qty через `int(tp_qty_raw / qty_step) * qty_step`
   - INSERT в `real_trades` с `bybit_order_id = 'recovery-' || substring(gen_random_uuid()::text, 1, 36)` (varchar(50) лимит!), `entry_time` = Bybit `createdTime` в UTC, `strategy` — из close-row или дефолт TREND, `initial_qty=qty`, `tp_levels=jsonb с label/price/close_pct/qty`
3. После insert: ORPHAN-алерт замолчит на следующем reconciler-тике, BE-move-real подхватит, dust-sweep подберёт остатки.

**Связано с:**
- [[real-position-bybit-no-db]] — общий orphan-recovery template; этот файл — sub-case
- [[real_trades-truth]] — DB лжёт по real PnL, особенно когда residual висит
- [[dust-sweep]] — почему он молчит на этих случаях

**Code TODO (PLAN MODE):** заменить `status='closed'` на `status='closing'` пока `size>0` на Bybit, чтобы dust-sweep подхватил residuals автоматически. Файл: `src/order_executor_wrapper_v3.py:222`. Эта правка избавляет от ручных recovery в будущем.

**Recovery, выполненная 2026-05-17:** FARTCOINUSDT 148 @0.196 SL=0.18864 → real_trade id=181 (TREND), 5 TP-ордеров на Bybit (TP1=0.20797, TP2=0.21243, TP3=0.21509, TP4=0.22693, TP5=0.2365, по 29 каждый, 3 контракта runner). SOL/BCH residuals Артём закрыл руками через Bybit UI.
