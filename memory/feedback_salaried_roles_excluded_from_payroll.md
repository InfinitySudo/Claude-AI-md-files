---
name: OnTime salaried roles excluded from hourly payroll
description: SALARIED_ROLES={'delivery','service'} — их wage helpers возвращают None, чтобы все cost loops автоматом skipали этих людей
type: feedback
originSessionId: b3cbd579-83db-48e9-85ab-677bcc6f8cfe
---
В `/root/ontime/backend/main.py` константа `SALARIED_ROLES = {'delivery', 'service'}`. Обе wage функции — `_wage_for_user_on` и `_ts_wage_on` — first checkнут `users.role`, и если она в SALARIED_ROLES, return None. Так каждый existing cost-loop с pattern `if wage is None: continue` автоматом дропает этих людей.

**Why:** David Ivanets (delivery) и Andrei Meska (service) на фиксированной месячной зарплате через accounting, не через hourly payroll. Их часы × wage инфлэйтили labor cost везде — Delivery shift project sal $281, service tasks cost overstated, company salary YTD double-counted (one time через ontime, second time через accounting payroll).

**How to apply:**
- При добавлении новой роли которая на ЗП (а не часовая) — добавь в SALARIED_ROLES.
- Hours этих ролей всё ещё видны в timesheets / project allocation для visibility (полезно знать что человек был на site).
- Payroll.csv / qb-payroll.csv их **не** включают (wage=None → row dropped в `_aggregate_payroll`).
- Если потребуется per-person flag (не по всей роли) — пересмотрите логику: добавьте `roster.salaried INTEGER` колонку и checkайте её приоритетно перед role.
