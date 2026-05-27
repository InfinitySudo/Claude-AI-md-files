---
name: OnTime Billable Hours Dedup
description: report wins per (uid, day) — не per (uid, pid, day); человек не может быть на двух объектах одновременно
type: feedback
originSessionId: aa5a3209-7b62-49dc-af6d-fb5c255622f9
---
OnTime считает часы/cost по проектам и payroll через `_billable_hours_map(conn, company_id, date_from, date_to, project_id?)` в backend/main.py. Правило: если у воркера есть хоть один daily_report в этот день — sessions на ВСЕХ проектах в этот день игнорируются (это forgot-checkout / неотчитанный transfer). Sessions считаются только когда у воркера НЕТ ни одного отчёта в этот день.

**Why:** 2026-05-01 Артём заметил Pavlo Kosts = 17.8h на двух объектах в один день (report 9h на Bldg 600 + забытая session 8.8h на Bldg 700). Раньше правило было per `(uid, pid, day)` — отчёт на проект A не блокировал сессию на проект B. Это переплачивало воркерам в payroll и завышало labor cost проектов B.

**How to apply:**
- Хелпер: `_billable_hours_map` возвращает `{(uid, pid, day) -> hours}`. Все потребители часов/cost должны использовать его (НЕ ходить отдельно в `daily_reports` + `work_sessions`).
- Уже переведены: `_dashboard_period_totals`, `admin_dashboard` (project loop + top_workers_week), `enrich_project`, `project_budget`, `_aggregate_payroll` (значит payroll.csv + qb-payroll.csv), `timesheet/matrix` + `timesheet/by-allocation`, `team-history` (через SQL правку).
- НЕ переведены и не должны: `export_hours_csv` + `qb-time.csv` (это сырой sessions log, не money calc), `_find_missing_reports` (digest), `foremen/{fid}/team` weekly (просто session count под форменом).
- Открытые сессии: helper считает live минуты только если started_at сегодня. Если открыта со вчера или раньше — 0 минут (forgot-checkout, не биллим).
- Anomaly `session_other_project` в `/api/timesheet/anomalies` ловит именно такие случаи (session с >30 мин на проект A в день когда воркер сдал report на B).
- Cost = hours × `_wage_to_cost(_wage_for_user_on(uid, day), day)` — оба хелпера тоже в main.py рядом с `_billable_hours_map`.

**Известное последствие:** total hours/salary slightly UP (~0.3%) после фикса — в случаях где report.hours > session minutes (воркер сдал больше часов чем зафиксировал QR), report теперь truth. Раньше session перекрывал. Это правильное поведение: report = truth.

**Update 2026-05-04:** добавлен `UNIQUE INDEX ix_daily_reports_unique_per_day ON daily_reports(user_id, project_id, report_date)` (init+migration). POST `/api/reports` ловит `sqlite3.IntegrityError` → 409 с `{error:'report_exists', existing_report_id}`. Раньше повторный submit копился (Omelchenko 9.8+9.81 = 19.6h на одном проекте). Multi-project в один день (transfer flow) индекс НЕ блокирует — Bahrii 20 апр 9h+9h на двух bldg остаётся возможен.

**Update 2026-05-09:** добавлен `MAX_BILLABLE_DAY_HOURS = 12.0` cap. Bhawanpreet 2026-05-04 имел 9h Magna + 9h Sage 400 = 18h при 1 сессии (admin отредактировал второй report). Защита в двух местах: POST `/api/reports` 409 если `existing_other_projects_today + new > 12h` (transfer flow с `pending_transfer` bypass'ит, т.к. это legit split day), и `_billable_hours_map` pro-rata scales (uid, day) totals down если в DB всё-таки прокралось >12h. Это не блокирует Bahrii-style 9+9 transfer cleanup потому что transfer flow проходит через pending_transfer; жесткий cap ловит только дубли без transfer.
