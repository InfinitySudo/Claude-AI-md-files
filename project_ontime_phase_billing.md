---
name: project_ontime_phase_billing
description: "OnTime — граница фазы проекта почасовка→установка (install_start_date); часы до даты биллятся по ставке, с даты жгут бюджет"
metadata: 
  node_type: memory
  type: project
  originSessionId: b354475f-dafb-44cb-81e4-96365d15d001
---

OnTime, 2026-06-11: проект может идти в две фазы, граница — поле `projects.install_start_date` (TEXT ISO, NULL = без сплита).

- Часы на днях **<** install_start_date = **почасовка/preп**: earned = часы × `hourly_billing_rate` (T&M-выручка, без капа).
- Часы **>=** даты = **установка**: earned по установленным материалам (кап budget_usd); и ТОЛЬКО эти часы жгут бюджет (Burn vs budget).
- Без даты, но со ставкой → legacy: ставка на ВСЕ часы (чистая почасовка, напр. RimRock). Не сломано.

Хелпер `_is_prep_day(day, switch)`. Применено в 3 местах P&L (держать синхронно!): `_serialize_project` (карточки/дашборд, поля prep_hours/install_hours/prep_billed/install_cost/budget_burn_pct), `/api/projects/{id}/budget` (BudgetPanel, поля prep_*/install_*), `/api/timesheet/by-allocation` (поля prep_cost_usd/install_cost_usd, копит proj_prep_hours/proj_prep_cost). Фронт: TimesheetPage burn = install_cost_usd когда дата задана; ProjectForm — поле даты при включённой почасовке. Поле в pydantic `ProjectUpdate` (PATCH пишет generically).

Forest Lawn (id 78): ставка $45, install_start_date=2026-06-11 → preп 160ч=$7201 выручка, result +$1914 (было −$5257), install burn 1.2%.

Связано: [[project_ontime_wage_cost]] (_wage_to_cost), [[feedback_billable_hours_dedup]] (_billable_hours_map — источник часов by-day), [[project_tsa_daily_reports]].
