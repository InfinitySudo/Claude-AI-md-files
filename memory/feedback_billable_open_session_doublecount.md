---
name: _billable_hours_map already projects open sessions
description: Не считать today_open отдельно поверх bmap — _session_minutes_safe уже возвращает live минуты для open sessions
type: feedback
originSessionId: b3cbd579-83db-48e9-85ab-677bcc6f8cfe
---
`_billable_hours_map(conn, ...)` для каждого open `work_sessions.ended_at IS NULL` row, через `_session_minutes_safe`, добавляет проектируемые минуты `(now − started_at)` в bmap. То есть текущий рабочий день (live) уже включён в bmap для открытой сессии.

**Why:** 2026-05-09 OT-status endpoint считал `today_done = today_closed + today_open`, где today_closed = сумма bmap-entries за сегодня, today_open = отдельный SELECT по open sessions. Открытая сессия попадала и сюда и сюда → 2× double count. Illia в 10am показывал 5h58min при реальных 3h2min с 7am.

**How to apply:**
- Любой эндпоинт показывающий "часы за день" должен использовать **либо** bmap **либо** напрямую work_sessions, не оба.
- `_session_minutes_safe` правило: closed → `duration_minutes`, open started today → live `(now − started_at)`, open started before today → 0 (forgot-checkout).
- Для бейджа "is_working_today" использовать отдельный set от `SELECT DISTINCT user_id WHERE ended_at IS NULL` — это про "прямо сейчас на сайте", не про hours.
- При проверке UI на double counts: сравнить bmap output с тем что показывает endpoint. Если расхождение — проверить нет ли поверх bmap отдельных pass'ов которые суммируют те же часы повторно.
