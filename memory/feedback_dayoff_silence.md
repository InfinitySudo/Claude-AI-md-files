---
name: OnTime: silence all nudges on company days off
description: 0 чекинов за 24ч = выходной → ни digest'ов, ни напоминалок никому. Хардкод-календарей нет, гейт через _company_had_activity_24h
type: feedback
originSessionId: 76d69d60-e032-4a5a-9b40-2a8d16aee677
---
В OnTime все cron-периодические уведомления (Director digest 08:00, Daily report nudge 18:00, Stale shortage nudge 18:00) обязаны проходить через гейт `_company_had_activity_24h(conn, company_id)` (`backend/main.py`). Гейт возвращает `True` только если в последние 24ч кто-то в компании сдал `daily_report` (hours>0) или начал `work_session`. На выходных и праздниках сигнал = `False` → никто (ни руководство, ни работники) не получает ни одного пинга от системы.

**Why:** Артём 2026-05-03: «чтобы отчёты, дайджесты и напоминалки не мозолили глаза в дни когда в компании выходной — ни руководству, ни рабочим». До фикса digest рассылал "Worked today: 0 · Everyone submitted ✓" каждое воскресенье, и stuck-EW пинги тоже шли в weekend — это тренирует получателей мьютить бот.

**How to apply:**
- При добавлении новой company-wide cron-напоминалки в backend (TG/notify): первой проверкой ставить `if not _company_had_activity_24h(conn, co['id']): continue`. Per-user briefings (driver morning briefing) self-gate через наличие задач — отдельный гейт не нужен, но и не повредит.
- Stuck/escalation override НЕ добавлять — Артём явно отверг этот компромисс. Stuck-item подождёт до первого рабочего дня; всё равно действовать на нём в выходной никто не будет.
- Хардкод календарей выходных (Sat/Sun, праздники, статутные holidays) НЕ нужен — сигнал «компания работает» = «кто-то реально чекинится». Если бригада решит выйти в субботу — бот сам заговорит, без правок таблицы holidays.
- Manual trigger endpoint `/api/admin/run_daily_report_nudge` возвращает `{skipped: 'no_activity'}` для skipped-компаний — использовать это в QA.
