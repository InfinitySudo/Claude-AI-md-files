---
name: OnTime Daily Report Nudge
description: Auto-alert 18:00 Calgary: кто работал, кто не подал daily report. Админ + форман своих объектов.
type: project
originSessionId: 4b6d419d-77a5-4a2e-95ea-6acfe740f2ee
---
**Что делает:** раз в сутки в 18:00 America/Edmonton процесс `ontime-api` сверяет `work_sessions` за «сегодня» (Calgary day) vs `daily_reports` с той же датой и шлёт TG-сообщение:
- **Админам компании** (`users.role='admin'` с `tg_chat_id`) — полный список `(worker, project, hours)` по всей компании.
- **Форманам** (`role='foreman'`) — только те строки, где `projects.foreman_id = foreman.id`. Если у формана всё подано — сообщение не шлётся.

**Why:** форманы и так в курсе своей бригады, но забывают проверять факт подачи отчёта. Артём просил не только ему, а каждому форману — чтобы не быть единственным «полицейским».

**How to apply:**
- Таймер живёт внутри async-задачи `_daily_report_nudge_loop()` в `backend/main.py` (рядом с `sweep_stale_sessions` loop'ом, стартует через `@app.on_event('startup')`). DST-safe — пересчитывает `target` при каждой итерации через `zoneinfo`.
- Ручной триггер: `POST /api/admin/daily-report-nudge/run` (require_admin). `?dry_run=true` — вернуть JSON без отправки TG.
- Сообщение **plain-text**, без Markdown — имена проектов содержат `_` (напр. `Magna_Bldg_1_...`), которые ломают Telegram Markdown.
- Helper в `notify.py` — `send_to_chat(..., parse_mode=None)` отключает парсинг.
- Константа `DAILY_NUDGE_HOUR = 18` в `main.py` — если захочет сдвинуть время, править там.

**Покрытие:** считает только сессии, где `started_at` попадает в Calgary-день. Открытые сессии (без `ended_at`) дают hours=0.0 в сообщении — это OK для напоминалки, но если будет раздражать, посчитать `COALESCE(duration_minutes, (now - started_at))` в SQL.
