---
name: OnTime Overtime Watch
description: PP-hours индикатор и forecast 88h/PP — куда смотреть и как алерт работает
type: project
originSessionId: 656b7c75-d454-4ed9-a10e-fd40c758b37e
---
TSA week = Mon-Thu 9h + Fri 8h = 44h × 2 = **88h/pay-period = OT_THRESHOLD_PER_PP**. Всё что сверху — 1.5×.

**Backend (`/root/ontime/backend/main.py`):**
- `GET /api/payroll/ot-status` — для каждого in-scope worker'а: `pp_hours`, `today_hours_done`, `today_hours_planned` (через `_workday_hours_for(today)`), `pp_forecast`, `ot_today_forecast = max(0, pp_forecast - 88)`.
  - Scope: finance/admin → вся компания; foreman → только свой crew по `project_installers` активных проектов; иначе только сам себя.
- `_maybe_send_ot_alert(conn, user_row, project_row, today)` — после успешного `/api/checkin` шлёт TG admin'ам если forecast > 88. Idempotent через таблицу `ot_alerts(user_id, day) UNIQUE`.

**UI:**
- `TimesheetPage.jsx` — `<OTPanel>` сверху, всегда виден (тихо скрывается при 403). Показывает только flagged workers (forecast OT > 0 или pp_hours ≥ cap), fallback — топ 8.
- `ProjectDetailPage.jsx` — `<OTChip>` рядом с каждым crew row (foreman/helper/installer); tooltip с PP/cap + today planned + forecast OT.

**Why:** Артём попросил 2026-05-05: «индикатор переработки 88h/PP + опoвещение об overtime forecast». Без TG-alert'а админ узнавал о OT только при выгрузке payroll.csv в конце PP — поздно.

**How to apply:** Если меняешь правила OT (cap, multiplier, weekday-таблицу) — синхронно правь `OT_THRESHOLD_PER_PP`, `_workday_hours_for`, и `_aggregate_payroll` (CSV). Frontend читает `pp_threshold` из ответа, так что динамика OK. Если добавишь worker-self view — скип scope-проверки только для запросов с `user_id == user['id']`.
