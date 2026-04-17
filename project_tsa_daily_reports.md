---
name: OnTime Daily Reports & Budget Analytics
description: Архитектура dailу-отчётов, budget analytics, team history в OnTime (после миграции 2026-04-17)
type: project
originSessionId: 7307290c-93f4-4995-a318-269609a49e02
---
**Таблицы в OnTime (`/root/ontime/backend/tsa.db`):**
- `daily_reports`: user × project × date, hours, notes. One-row-per-shift.
- `daily_report_items`: report_id × material_id × quantity + **unit_price_snapshot** (цена на момент отчёта, не текущая).
- `project_materials`: project × material + planned_qty (из формы проекта).
- `materials.unit`: ea/sft/lft/m/m2/kg/bag/box/sheet.

**Правила часов (dual-source, без двойного счёта):**
- За день: отчёт выигрывает. Если `daily_reports` для (user, project, date) есть — часы берём оттуда, игнорируя `work_sessions` того же дня.
- Если отчёта нет, но сессия есть — считаем сессию.
- Реализовано в `enrich_project` через `NOT EXISTS` JOIN.

**Edit policy:** отчёт правится/удаляется только в день его создания. Admin — всегда. Enforce в `_report_is_editable`.

**Ключевые эндпоинты:**
- `GET /api/reports?project_id&user_id&date_from&date_to` — фильтр по роли: installer видит свои; foreman — свои + проектов, где он primary.
- `GET /api/projects/:id/budget` — spent_labour, spent_materials, forecast_total, overrun_flag, per-material progress.
- `GET /api/projects/:id/team-history` — per-user hours/labour/materials на проекте.
- `GET /api/reports/prefill/hours?date&project_id` — prefill часов из сессий.

**Формулы:**
- `hours_budget_calc = budget_usd / avg_crew_wage` (не хранится, считается on-the-fly в `_hours_budget_from_crew`). Используется когда `projects.hours_budget = 0`.
- WORKDAY_HOURS = **9.0** (Alberta), не 8. Критично для любых расчётов дней-нужно.
- `forecast_total = daily_burn_rate × total_days` → overrun если > budget_usd.

**UI:**
- `/daily-reports` — список с фильтрами; `/daily-reports/new|:id` — форма.
- ProjectDetail: `BudgetPanel` + `TeamHistoryPanel` (admin + primary foreman).
- ProjectsPage cards: workers_count, reports_count, materials_installed_cost, last_activity.

**Why:** Заменили Django+TG-бот+Google Sheets старой TSA-системы.

**How to apply:** Не пихать часы в оба источника (`work_sessions` + `daily_reports`) одновременно — dedup построен на дате+user, так что дублирование в один день не страшно, но в разные дни одного workday (редкий кейс) удвоит. При добавлении новых агрегатов — всегда учитывай dual-source.
