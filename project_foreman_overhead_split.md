---
name: OnTime Foreman Overhead Split (Variant B, since 2026-01)
description: Primary-foreman cost вынесен в company overhead, project P&L = earned − crew salary; cutoff 2026-01-01; only users.role='foreman'
type: project
originSessionId: b3cbd579-83db-48e9-85ab-677bcc6f8cfe
---
С 2026-05-09 OnTime считает project labour cost иначе:

**Раньше:** `salary` = sum hours × wage всех на проекте, `result` = earned − salary. Foreman'ы топили проекты в loss.

**Сейчас (Variant B):**
- `salary` (per-project и company-wide) = только crew (без primary foreman'a)
- `foreman_overhead` = primary foreman cost того же периода — отдельная строка company overhead
- `result` = earned − salary (БЕЗ foreman'a) — project operational P&L
- `salary_with_foreman` / `result_with_foreman` = full P&L (legacy)
- Cutoff `FOREMAN_OVERHEAD_CUTOFF = '2026-01-01'` — pre-2026 days считаются по-старому (legacy reports не ломаются)

**Helper functions** (`backend/main.py`, рядом с SALARIED_ROLES):
- `_foreman_history_map(conn)` — pid → [(foreman_id, from_date, to_date)]; читает `project_foreman_history` + fallback на `projects.foreman_id` для проектов без history; **filters только** users.role='foreman' (installer-as-temp-lead → НЕ overhead, его hours идут в crew); synthetic prepend [1970..earliest_from-1] для покрытия pre-history period
- `_is_project_foreman_on(map, uid, pid, day)` — True только если day >= cutoff AND uid в map для pid на этот day

**6 endpoints используют этот split:**
- `enrich_project` — для /api/projects, /api/projects/{pid}
- `project_budget` — /api/projects/{pid}/budget
- `admin_dashboard` — /api/admin/dashboard (per-project + company totals)
- `_dashboard_period_totals` — Custom range / YTD / period
- `_dashboard_monthly_breakdown` — Year by month bars
- `timesheet_by_allocation` — /api/timesheet/by-allocation (создаёт виртуальную группу "Foreman cost (overhead)")

**Validation** (с 2026-05-09):
- POST `/api/projects` и PATCH `/api/projects/{pid}` reject foreman_id если users.role != 'foreman' (return 400 `foreman_role_required`). Project lead должен быть real foreman, иначе нельзя.
- One-shot 2026-05-09: 47 legacy non-foreman rows удалены из project_foreman_history (все associated projects были done; backup `tsa.db.bak-before-pfh-cleanup-*`).

**Payroll.csv не тронут** — foreman всё ещё получает свою выплату через payroll, classify-only в analytics.

**UI отображение:**
- BudgetPanel: `Salary $X` + amber `+ $Y foreman (overhead)`. Если у проекта primary foreman set но он не QR'ился (overhead=0), показывается серый italic `+ $0 foreman (no on-site hours)` — чтобы было видно что split применён.
- ProjectsPage cards / Dashboard active project rows: `earn $X · sal $Y / $budget · +$Z fmn` (amber chip когда > 0)
- Dashboard top stats / Salary YTD / Custom range: amber `+ $Y foreman overhead` под salary value
- i18n keys: `bud_foreman_overhead`, `bud_foreman_overhead_zero`, `dash_foreman_overhead`

**How to apply:**
- При добавлении новых endpoint'ов которые считают labor cost — вызывать `_is_project_foreman_on(fh_map, uid, pid, day)` в loop и dispatch cost в crew vs overhead bucket.
- НЕ возвращать back в "all-in-one salary" логику — это сознательное решение Артёма для visibility операционной эффективности команды vs management overhead.
- Если придётся добавить новую роль которая тоже должна считаться overhead (pm/vp/director как foreman'ы on-site?) — расширь `_is_foreman` lambda в helper.
- Variant C (foreman monthly_salary distributed proportionally) — обсуждалось, не реализовано; для перехода нужна `users.monthly_salary` колонка + per-month redistribution.
