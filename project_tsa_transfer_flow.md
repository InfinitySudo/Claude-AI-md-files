---
name: OnTime Worker Transfer Flow
description: Перемещение работника между active projects идёт ТОЛЬКО через transfer-flow с обязательным daily_report по исходному bldg
type: project
originSessionId: 2698e6df-f89c-4d5c-ae55-ba7c1be6f1d9
---
С 2026-04-27: добавлен `pending_transfers` flow вместо старого `_detach_worker_from_other_active_projects` каскада, который сносил рабочих из crew без следа.

**Why:** Старая логика one-active-project каскадно убирала worker'а из всех других active project'ов при любом add_helper/add_installer. Igor K жаловался: «утренние списки к вечеру разваливаются». Артём решил: чтобы часы и материалы оставались привязаны к bldg где был чекин, перевод только через явный transfer + report.

**How to apply:** При работе с crew assignments:
- `add_helper` / `add_installer` / PATCH `/projects` (installer_ids) теперь возвращают **409 transfer_required** если worker в active crew другого проекта (см. `_other_active_membership` в main.py).
- Перемещение: `POST /api/workers/{uid}/transfer-request` body `{ from_project_id, to_project_id }` — фиксирует slot ('installer'|'helper') и helper_role, шлёт TG + bell-нотификацию работнику.
- Когда worker делает `POST /api/reports` по `from_project_id` — `_apply_pending_transfer` атомарно detach-ит из from + attach к to + проставляет `daily_reports.kind='transfer'`.
- `_force_detach_worker_company_wide` оставлен в коде, но НЕ вызывается из add-эндпоинтов — только future use.
- Stale-nudge: `nudge_stale_transfers` бежит в общем sweep loop (60s), один раз пингует worker+foreman через 1ч если report не сдан.
- Cancel: `DELETE /api/workers/{uid}/transfer-request` (foreman/admin/worker сам).

**Frontend triggers:**
- Кнопка ↪ ArrowRightLeft в crew-list `ProjectDetailPage` (только foreman/mgmt).
- Banner в `InstallerHomePage` если есть `myPendingTransfer` — кнопка ведёт на `/daily-reports/new?project_id=<from>`.
- Chip `awaiting_report_to` рядом с work-row на проекте (загружается через `api.projects.pendingTransfers(id)`).

**i18n keys (en/ru/uk):** transfer_worker, transfer_requested, transfer_explainer, request_transfer, awaiting_report_to, to_project, from, pending_transfer_banner, submit_report_now, cancel_transfer.

**Schema additions:**
- `daily_reports.kind` TEXT DEFAULT 'eod' ('eod' | 'transfer').
- `pending_transfers` table с unique active index на user_id (один pending на работника).

**Backfill решение:** оставлены как есть (Mykola Bahrii, Bhawanpreet, Yaroslav и др. что были оторваны 2026-04-27 утром). Дальше — всё под контролем формана.
