---
name: OnTime Timesheet Tab
description: /timesheet — единый контроль часов/cost по workers × days, allocation tree (project/service/delivery), anomalies feed. Доступ — hasFinanceView.
type: project
originSessionId: aa5a3209-7b62-49dc-af6d-fb5c255622f9
---
Артём попросил вкладку для контроля всех часов всех сотрудников по всем проектам/сервисам/доставкам. Реализовано 2026-05-01.

**Why:** одной точки наблюдения не было — DashboardPage показывает агрегаты по проектам, но не worker × day матрицу и не «куда ушли часы» в разрезе service+delivery. Аномалии (mismatch report vs session) тоже нигде не отображались.

**How to apply:**
- 3 view: `Matrix` (workers × days, цвет ячейки = source: emerald=report, amber=session-only), `By allocation` (project/service/delivery groups → workers), `Anomalies` (mismatch >1h, overlong >14h, report_no_session, session_no_report).
- Backend: `GET /api/timesheet/{matrix,by-allocation,anomalies}` в `backend/main.py` перед `/api/health`. Все три — `require_finance`. `_ts_wage_on(conn, uid, date)` берёт wage из wage_history (date-bounded) с fallback на roster.hourly_wage; `_wage_to_cost(wage, date)` даёт cost-with-burden.
- Source-of-truth для ячейки: report > session (тот же паттерн, что в `admin_dashboard`).
- Cell.allocations[] — массив проектов на день (worker может работать на нескольких объектах за день); drill-down модалка показывает разбивку.
- Service hours = `service_tasks.service_work_hours`, attributed к `completed_at` дате и `assignee_id`. Delivery hours = `delivered_at − started_at`, attributed к `assigned_to_user_id`.
- Frontend: `src/pages/TimesheetPage.jsx`, route `/timesheet`, кнопка в Header — Clock icon, видимость по `hasFinanceView(me)`.
- Lang keys префикс `ts_*` в `src/lib/i18n.js` (en/ru).
- Период max 92 дня (защита от тяжёлых запросов).

**Известное:**
- В апреле 2026 anomalies feed дал 431 `report_no_session` (отчёты сдают вручную или management вписывает hours без QR-сессий). Если Артём попросит — добавить toggle «скрыть report_no_session» или ослабить правило (например, не показывать когда отчёт от management-роли).
- Matrix не учитывает service/delivery hours в ячейках (избегаем double-count с project sessions). Service/delivery видны только в By Allocation view.
