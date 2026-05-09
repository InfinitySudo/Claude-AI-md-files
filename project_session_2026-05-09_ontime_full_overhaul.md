---
name: OnTime full hours/finance overhaul (2026-05-09 session)
description: Big-day rundown — что трогали в OnTime 2026-05-09: lunch bug → hourly billing → foreman overhead split → consistency fixes
type: project
originSessionId: b3cbd579-83db-48e9-85ab-677bcc6f8cfe
---
Огромная single-day session. Все изменения запушены в `InfinitySudo/OnTime`.

## Hours integrity (utro)
1. **Lunch для open sessions** — `_session_hours_authoritative` теперь вычитает 12:00-12:30 для open sessions тоже (раньше живая projection давала на 30 мин больше). Backfill 110 отчётов apr-may.
2. **`_refresh_same_day_report_hours`** в `_close_session` — пересчитывает report.hours при закрытии сессии. Guards: skip management overrides, skip если есть session >14h (forgot-checkout), skip если новое значение увеличивает hours >0.55h.
3. **MAX_SESSION_MINUTES=12h cap** в `_eod_cutoff_utc` — phantom overnight sessions (Yaroslav/Artem H) обнулены.
4. **LATE_CHECKIN_BLOCK 18:30** — блокировка QR-in после 18:30 local, management bypass.
5. **MAX_BILLABLE_DAY_HOURS=12** в `_billable_hours_map` + POST /api/reports — защита от 9+9=18h на двух проектах в один день.
6. **switched_project session counts если нет report на тот project** — закрыта дыра transfer flow без report on from-project.

## Hourly billing (середина дня)
1. `projects.hourly_billing_rate REAL` колонка добавлена.
2. **Combined mode**: `earned = min(materials_installed × price, bldg_cost) + (hours × rate)`. Pure-materials, pure-hourly, и combined — все работают через тот же formula. Один checkbox в ProjectForm "Hourly billing".
3. Применено в **6 endpoints**: enrich_project, project_budget, admin_dashboard, _dashboard_period_totals, _dashboard_monthly_breakdown, timesheet_by_allocation.
4. **3 проекта на $45/h**: RimRock (id=23), Arborn Lake Service (id=60), MG84 Columns Bldg 1-3 Extra Work Hours (id=69). Material rows зачищены — pure hourly mode для них.

## Foreman overhead split (Variant B, cutoff 2026-01-01)
- Memory: [project_foreman_overhead_split.md](project_foreman_overhead_split.md)
- Все 6 endpoint'ов exposes `salary_crew + foreman_overhead`, result = earned − salary_crew (без foreman'a)
- Validation: POST/PATCH /api/projects reject non-foreman foreman_id
- Cleanup: 47 legacy installer-as-lead history rows удалены
- UI: amber chip везде где видно salary
- Test Foreman архивирован (был attached к Bldg 21 + Faro Ihor Ch)

## Salaried roles
- Memory: [feedback_salaried_roles_excluded_from_payroll.md](feedback_salaried_roles_excluded_from_payroll.md)
- David Ivanets (delivery) и Andrei Meska (service) исключены из cost loops

## OT panel + Anomalies (диагностика)
- Lunch double-count в payroll_ot_status (3h+3h=6h) → fix: убрал отдельный today_open pass, bmap уже включает open session live minutes.
- ZoneInfo import добавлен (Anomalies tab крэшилась).
- Sort fix: workers on site сначала, потом OT risk.

## UI fixes
- Live "Currently on site" вместо retrospective 24h в director digest.
- "Xh Ymin" формат глобально (`fmt.js` updated).
- ProjectsPage cards: `earn $X · sal $Y / $budget · +$Z fmn` chip.
- Dashboard top stats: foreman overhead amber line.
- BudgetPanel: foreman row показывается всегда (когда есть primary foreman set), `+ $0 (no on-site hours)` для not-on-site.
- ProjectForm: "— No primary foreman (installer leads) —" option.
- Year 2025 monthly bars + per-project breakdown card на dashboard.

## Workflow features
- **Auto-pull worker on add** при 409 — foreman target кликает Save → backend сразу запускает full pull-now (close session, synth auto_transfer report, swap crew slot, notify both foremen).
- **Pending reports today** — `GET /api/me/pending-reports-today` + UI banner на InstallerHomePage + 30-min EOD reminder loop (17:00-22:00 Calgary).

## Bug fixes
- **canonical_id double-count в project_budget orphan branch** — items с canonical_id указывающим на BOM material считались дважды (через alias UNION + orphan). Project earned был inflated на $2.8k для MG84 Bldg 20. Fix: orphan теперь exclude'ит canonical-aliased items.

## Backups
Несколько: `tsa.db.bak-before-livingston-backfill-*`, `tsa.db.bak-before-aprmay-lunch-backfill-*`, `tsa.db.bak-before-phantom-cleanup-*`, `tsa.db.bak-before-rimrock-hourly-*`, `tsa.db.bak-before-pfh-cleanup-*`, `tsa.db.bak-before-test-foreman-cleanup-*`.

## Open follow-ups
- Variant C для foreman overhead (proportional monthly_salary) — обсуждалось, не реализовано
- Bulk endpoint для report move (если потребуется массово переносить)
- pm/vp/director — сейчас обычная команда; если на ЗП через accounting → расширить SALARIED_ROLES
- 33 done legacy projects с installer-as-lead — оставлены как есть (не аффектит after my fixes)
