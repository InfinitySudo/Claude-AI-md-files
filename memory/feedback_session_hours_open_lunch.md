---
name: OnTime _session_hours_authoritative open-session lunch
description: Open-session live projection MUST subtract 12:00-12:30 lunch like closed sessions, иначе reports разъезжаются от payroll
type: feedback
originSessionId: b3cbd579-83db-48e9-85ab-677bcc6f8cfe
---
В `backend/main.py::_session_hours_authoritative` для open-session ветки (`ended_at IS NULL`) обязательно вычитать `_break_deduction_min(started_at, now_iso, project_tz)`. Closed-session ветка использует `duration_minutes`, который уже net of lunch (`_close_session` минусует обед). Если открытую считать как `now − started_at` без вычета — installer, сабмитнувший отчёт ДО QR-out, получит hours на 30 минут больше, чем сабмитнувший ПОСЛЕ. На Livingston Bldg A 2026-05-08 это дало разброс 8.03 vs 8.55 у людей, начавших одну смену вместе.

**Why:** 2026-05-09 фореман Livingston пожаловался "все check-in'ились в одно время, а часы разные". Корень — этот баг + auto_checkout_eod хвост.

**How to apply:**
- При любом изменении `_session_hours_authoritative` обе ветки должны быть консистентны по обеду.
- `_close_session` теперь зовёт `_refresh_same_day_report_hours(conn, session_id, started_at)` — пересчитывает report.hours для (user, project, date) если автор не management. Management reports могут нести ручной hours-override и не трогаются.
- Если добавляешь новый close-path для work_sessions — ОБЯЗАТЕЛЬНО позови `_refresh_same_day_report_hours` иначе старый bug вернётся через закрытие через side-channel.
- Backfill старых отчётов: `UPDATE daily_reports SET hours = SUM(work_sessions.duration_minutes)/60` per (user, project, date), но только для non-management ролей.
