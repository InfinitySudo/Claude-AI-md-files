---
name: logger-utc-label-must-match
description: "logger.py — formatter.converter = time.gmtime обязательно, иначе datefmt '... UTC' пишет local time (MDT) под видом UTC. 6h дрейф."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

## Правило

В `/root/4BotsBybit-Trading/src/logger.py`:

```python
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S UTC'
)
formatter.converter = time.gmtime   # ← без этой строки suffix врёт
```

**Why:** `asctime` по умолчанию использует local time (server в `America/Edmonton`, MDT = UTC-6). Hardcoded суффикс " UTC" в datefmt не превращает время в UTC. До 2026-05-16 (commit `211f9b8`) логи писались как `2026-05-16 01:41:45 UTC` хотя реально 01:41:45 MDT = **07:41:45 UTC**.

Это привело к 6-часовому silent дрейфу: DB `closed_at` writes `datetime.utcnow()` (правильный UTC), логи писали local. При расследовании инцидентов time-alignment между DB и логами требовал вручную добавлять 6h.

**How to apply:** любой новый Python project на этом VPS — `formatter.converter = time.gmtime` для любого logger.Formatter, который маркирует UTC. Иначе timezone-trap.

## Side-check

После рестарта `journalctl -u bybit-tradingbot --since '1 min ago'` должен показывать timestamp совпадающий с `date -u`. Дрейф = bug.

## Server timezone (server-level)

`America/Edmonton` (MDT, UTC-6 / UTC-7 with DST). См. [[feedback-systemd-oncalendar-local-time]] про OnCalendar для cron.

## Связано

- [[feedback-sqlite-isoformat-trap]] — другой timestamp trap
- [[feedback-systemctl-timestamp-js]] — formatting timestamps for browser
- [[feedback-systemd-oncalendar-local-time]] — server в MDT
