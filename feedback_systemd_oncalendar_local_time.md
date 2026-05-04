---
name: systemd OnCalendar = local time, не UTC
description: 2026-05-02 — попался: написал OnCalendar=18:00 думая UTC, systemd интерпретировал как local (Calgary MDT) → срабатывало в 6pm вместо ожидаемого
type: feedback
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
**Правило:** `OnCalendar` в systemd timer'ах по умолчанию = **локальное время сервера**, не UTC. Сервер Артёма стоит в `America/Edmonton` (MDT/MST в зависимости от сезона).

**Why:** При правке `bybit-claude-hourly.timer` я написал `OnCalendar=*-*-* 18:00:00` рассчитывая что это UTC (server timezone-aware), а интерпретировалось как 18:00 MDT = 00:00 UTC. Если хочешь полдень Calgary → пиши `12:00:00`.

**How to apply:**
1. **Быстрая проверка**: `systemd-analyze calendar "<expr>" --iterations=3` показывает Next в обоих TZ — local и UTC
2. **Verify после правки**: `systemctl list-timers <name> --no-pager` — колонка NEXT в local time
3. **Чтобы зашитить как UTC**: добавить параметр `OnCalendar=UTC *-*-* 18:00:00` (с префиксом TZ)
4. **Calgary cheat**: MDT = UTC-6 (лето), MST = UTC-7 (зима, ноябрь-март)

**Текущие OnCalendar в trading проекте (после 2026-05-02 правок):**
- `bybit-claude-hourly.timer` → `*-*-* 06,18:00:00` (2×/день Calgary, утро+вечер)
- `bybit-claude-watchdog.timer` → `*-*-* 06,12,18,22:00:00` (4×/день Calgary)

Все другие timer'ы на VPS (TSA/OnTime nightly sync, daily nudge, Roofmart catalog) — стоит проверять при правке: вряд ли они в UTC если описание говорит «Calgary».
