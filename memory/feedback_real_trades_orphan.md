---
name: Real position on Bybit with no real_trades row
description: Kogda na Bybit est' real pozicia a v real_trades pusto — znachit place_order_from_signal vernul success=False do insert. Proveryat' cherez ByBit API, vstavlyat' row rukami, chinit' bug.
type: feedback
originSessionId: a50e8fb7-4ba7-4e12-826b-ccf591fe559e
---
**Симптом:** отчёт / dashboard `?source=real` говорит `open: 0`, а на Bybit реально открытая позиция.

**Что проверить:**
1. `bybit_api.ByBitAPI.get_open_positions()` (нужен clean env, `env -i PATH=/usr/bin python3 ...` т.к. у моей shell-сессии мог быть обрезанный `BYBIT_API_KEY`).
2. `SELECT * FROM real_trades WHERE status='open';` — если пусто, бот слеп.
3. `journalctl -u bybit-tradingbot` на время открытия позиции: искать `SL/TP setup FAILED` / `UNPROTECTED` / `Side 'SELL' invalid` — признак что `place_order_from_signal` вернул до `db.insert_real_trade`.

**Root cause (2026-04-22 XLMUSDT):** в `order_executor_wrapper_v3.py` `if not stop_loss_result.get('success')` тригерил safety-close даже при BE-fail с установленным SL; close-path передавал `side='SELL'` в `validate_order` (принимает только LONG/SHORT) → close провалился → `return order_result` до insert.

**Fix:** safety-close только при `not sl_set` (`stop_loss_result.get('sl_order_id')` отсутствует). BE/TP partial errors = warning, `order_result['partial_tp_be']=True`, код идёт дальше к `insert_real_trade`. При close использовать `direction in {LONG, SHORT}`, не `SELL/BUY`.

**Recovery:**
- Вставить потерянную строку руками:
  ```sql
  INSERT INTO real_trades (symbol, direction, entry_price, qty, sl_price,
    bybit_order_id, entry_time, strategy, fees_paid_usd, status, created_at, updated_at)
  VALUES ('XLMUSDT','LONG',0.17523,473,0.17327,
    '<uuid>', '2026-04-22 23:16:35.435342', 'TREND', fees_calc, 'open', NOW(), NOW());
  ```
  Entry price и qty брать из `get_open_positions().avgPrice / size` (actual fill, не signal).
- Рестарт TradingBot (подхватит для monitor/reconciler).

**Why:** Без real_trades-строки drawdown guard, hourly report, dashboard и hybrid-routing теряют видимость реальных позиций. При очередном сигнале dup-check может открыть дубль.
