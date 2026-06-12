---
name: feedback_manual_ticket_sl_race
description: Manual-тикет pumpdump ставил вход place_entry без подтверждения филла → SL race 10001
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5953d251-e235-4db9-839e-85e0af7d45ee
---

PumpDumpAI_Agent (`pumpdump.service`, «Trading Panel + AI Tools», Bybit **sub-4**, REAL; код `/root/PumpDumpAI_Agent/src/main.py` + `executor.py`). НЕ путать с 4BotsBybit-Trading — живой ticket-панель и sub-4 ключи здесь (e2KP...). Панель pumpdump.html на :8080.

**Баг 2026-06-12 (BTCUSDT/CLOUSDT остались без SL):** manual-тикет `_open_manual_position` ставил вход через `place_entry` (возвращает OK по ACK, НЕ ждёт филла) → `set_trading_stop` вызывался при size=0 → Bybit `10001 "can not set tp/sl/ts for zero position"` → SL не вставал; аварийное закрытие тоже гонялось с незаполненной позицией.

**Why:** авто-путь давно использует `open_confirmed` (ждёт size>0 через `_await_fill`), а manual-ticket — нет. Регресс именно на ручном пути.

**How to apply / fix (commit 02a603d):** `_open_manual_position` → `open_confirmed` вместо `place_entry`; `_set_sl_market_retry` ретраи 6→10. Watchdog (30с, `tracker.watchdog_check`) = бэкап 100%-SL: закрывает позицию ТОЛЬКО если `stopLoss=0` (позиция с SL не трогается).

**Ручная постановка SL на живую позицию** (read-only + set): загрузить `/root/PumpDumpAI_Agent/.env` в os.environ → `Executor('REAL',{})` → `get_open_positions()` (проверить `stopLoss`), `force_sl(sym, side, qty, sl_price)` → verify повторным `get_open_positions`. См. [[feedback_sl_zero_position_race]], [[feedback_real_sl_qty_step]], [[feedback_conditional_order_cleanup]], [[feedback_bybit_migration_bypass]] (close-real только с явного разрешения; SL ставить — ок).
