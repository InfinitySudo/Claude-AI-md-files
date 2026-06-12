---
name: feedback_conditional_order_cleanup
description: conditional SL/TP через order/create не чистятся set_trading_stop(null); SL_VERIFY слеп к Limit-SL → дубли ×3 + сироты; fix fec3f90
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bdb4f909-54ef-4bf6-860a-d1df635c78bf
---

В 4BotsBybit-Trading SL/TP ставятся **standalone conditional-ордером** через `/v5/order/create` (`place_sl_trigger_order`/`place_tp_trigger_order`). Две ловушки, из-за которых у real-трейдера F накопились 9 сирот (BNB/BCH/ETH ×3) на закрытие уже несуществующих шортов:

1. **`set_trading_stop(sl=None,tp=None)` чистит только position-attached TP/SL, НЕ conditional из order/create.** «Clear old TP/SL» в `order_executor_v3.set_position_stop_loss` не убирал старые conditional.
2. **SL_VERIFY (`order_executor_wrapper_v3` ~1261) проверял наличие SL только по `position.stopLoss`** — а оно пусто при SL=**Limit** (maker, движок cons). → verify «не видит SL» → ретраит `set_position_stop_loss` 3× → **3 идентичных дубля** (тайминги совпадают до секунды).
3. **Reconciler при пустом `closed_pnl` делал `continue`** (позиция ушла, но нет записей PnL) → строка `real_trades` висит `open`, conditional не отменяются.

**Why:** reduce-only сироты без позиции не тратят деньги, но при НОВОМ шорте на том же символе могут подрезать позицию не на том уровне + упор в лимит Bybit 20 conditional/символ + перекос статистики (orphan_db_no_bybit).

**How to apply:** для conditional-ордеров отмена — `ByBitAPI.cancel_conditional_orders(symbol)` (cancel-all `orderFilter=StopOrder`), НЕ `set_trading_stop(null)`. Проверка наличия SL должна учитывать conditional StopOrder (SL vs TP различать по `triggerDirection`: LONG SL=2 / SHORT SL=1). Reconciler закрывает сирот по грейсу 30мин. Fix commit `fec3f90`.

Связано: [[project_session_2026_06_05_real_sl_promoter]], [[feedback_real_sl_qty_step]], [[feedback_bybit_tp_limit_quirks]].
