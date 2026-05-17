---
name: orphan-safety-nets
description: 4 surfaces preventing orphan positions / missing-SL in main TradingBot (sub1) — added 2026-05-16 after $79 orphan-position incident.
metadata: 
  node_type: memory
  type: project
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

В `/root/4BotsBybit-Trading/` (commit `a7420cc`, 2026-05-16) добавлены 4 safety nets чтобы:
1. Позиции на Bybit без DB-row не накапливались незаметно
2. Open позиции без SL не существовали
3. Dust-остатки не блокировали новые сигналы
4. Failed insert'ы не молчали

## 1. STEP 1B dust filter — `main_bot_v3.py:692`

```python
DUST_NOTIONAL_USD = 2.0
if pos['qty'] * pos['current_price'] < DUST_NOTIONAL_USD:
    skip from dup-count
```

Dust (<$2 notional) на Bybit больше не блокирует новые signals на символе. Bybit One-Way Mode при новом open агрегирует — dust растворяется в avgPrice.

## 2. Reconciler reverse-loop — `order_executor_wrapper_v3._detect_orphans_and_missing_sl`

После основного DB→Bybit loop каждые 60s:
- **Orphan**: live_pos с size>0 но без DB-row → TG-alert + log (per-symbol 1h cooldown в `_orphan_alert_at` dict).
- **Missing SL**: known DB-trade у которого `live_pos.stopLoss` пустой/0 → TG-alert (per-trade-id dedup в `_missing_sl_alert_ids` set).

Alerts через `telegram_notifier_v3.send_alert(text)` (module-level helper, использует `TELEGRAM_REPORT_BOT_TOKEN` + `TELEGRAM_CHAT_ID`).

## 3. SL post-place verification — `order_executor_wrapper_v3.place_order_from_signal`

После `set_position_stop_loss` returns OK:
1. Sleep 0.5s
2. Re-query `get_open_positions()` для symbol
3. Check `live_pos.stopLoss > 0`
4. Если empty: retry `set_position_stop_loss` × 2 with 1s sleeps
5. Если still empty: TG-alert + log `[NO_SL]`. **НЕ закрываем позицию автоматом** (per Артём, 2026-05-16) — оставляем открытой для ручного контроля.

## 4. insert_real_trade retry + dead-letter — `database_v3.py:499`

```python
def insert_real_trade(self, trade_data, _max_retries=3):
    for attempt in range(_max_retries):
        try: INSERT; return True
        except (OperationalError, InterfaceError): retry with backoff
        except Exception: break (no retry, permanent)
    self._write_failed_insert(trade_data, last_exc)
    return False
```

`_write_failed_insert` пишет в новую таблицу `failed_real_inserts` (id, attempted_at, trade_data JSONB, error_message, recovered_at, recovered_by) и шлёт TG-alert. Recovery вручную через SQL.

Migration: `scripts/migrate_failed_real_inserts.sql` (применён).

## What НЕ сделано

- **Auto-import orphans** — НЕТ. Только alert. Per Артём: synthetic-row с неправильной strategy attribution = риск, лучше ручной разбор.
- **Auto-close on missing SL** — НЕТ. Только alert.
- `_maybe_sweep_dust` НЕ расширен на orphan-positions (требует DB row).

## Тесты

`tests/test_orphan_detection.py` — 11 кейсов: dust filter, orphan alert + cooldown, missing-SL alert + dedup, insert retry, dead-letter.

## Recovery flow для dead-letter

```sql
SELECT id, attempted_at, trade_data->>'symbol' AS sym, error_message
FROM failed_real_inserts WHERE recovered_at IS NULL ORDER BY attempted_at DESC;
-- Поправь схему / constraint, потом:
UPDATE failed_real_inserts SET recovered_at=NOW(), recovered_by='manual' WHERE id=?;
```

## Связано

- [[feedback-real-trades-truth]] — orphans known issue
- [[feedback-real-trades-orphan]] — manual orphan insert pattern
- [[feedback-real-trades-fee-semantics]] — fee handling в reconciler
- [[feedback-bybit-ws-keepalive]] — другой safety net pattern
