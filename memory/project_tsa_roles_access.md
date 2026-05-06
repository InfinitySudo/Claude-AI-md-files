---
name: OnTime roles + access matrix
description: Management (pm/vp_construction/director) получают admin-equivalent capability во всём, кроме destructive и invite-code governance
type: project
originSessionId: f1c65322-19fe-4461-86eb-62acb1eaf226
---
OnTime роль-хелперы и матрица доступа — как расширялось в 2026-04-21.

**Backend helpers (`ontime/backend/main.py`):**
- `MANAGEMENT_ROLES = {'admin', 'pm', 'vp_construction', 'director', 'director_estimator'}` (line ~95).
- `require_management` (Depends) — для не-destructive mutation endpoints. Строго возвращает 403 для всех остальных.
- `_is_management(user)` — inline capability check. Использовать вместо `user['role'] == 'admin'` в capability-тестах (edit report, approve extras, override geofence, delete чужого фото и т.д.).
- `require_admin_or_accountant` — read access: admin/accountant/pm/vp/director (+не мутации). Accountant тоже здесь.
- `_has_finance_view(user)` — видит ли $-колонки: admin/accountant/pm/vp/director/purchasing_manager.

**Frontend helpers (`ontime/src/lib/roles.js`):**
- `isManagement(me)` — для UI gates: редактировать/создавать/аппрувить/override.
- `hasFinanceView(me)` — показать ли $-поля.
- `isAdminStrict(me)` — для destructive/governance кнопок (см. ниже).

**Admin-only (оставлено, НЕ расширено) — все DESTRUCTIVE:**
- `DELETE /api/projects/{pid}` (удалить проект — явно сказано Артёмом нельзя)
- `DELETE /api/roster/{rid}`
- `DELETE /api/materials/{mid}`
- `DELETE /api/projects/{pid}/materials/{mid}`
- `DELETE /api/lifts/{lid}`
- `DELETE /api/service-tasks/{tid}`
- `DELETE /api/tg-groups/{gid}`
- Hard-delete delivered delivery-task (`DELETE /api/delivery-tasks/{did}` со статусом `delivered`)
- `set_user_role` запрещён для users с role='admin' (нельзя отобрать admin через UI)
- TG WebApp `tg-auth` для instructions: gate расширен на MANAGEMENT_ROLES 2026-05-06

**Открыто management 2026-05-06 (раньше require_admin/require_admin_dep):**
- `DELETE /api/projects/{pid}/complete` (undo_complete, реверс completion проекта)
- `POST /api/admin/director-digest/run` + `/daily-report-nudge/run`
- `POST /api/vendors/bulk` (bulk_upsert_vendors)
- `PATCH /api/procurement-settings`
- Все instructions endpoints (`GET/PUT /api/instructions/*`, broadcast, recipients)
- Все TG-groups endpoints, КРОМЕ `DELETE /api/tg-groups/{gid}` (всё ещё admin)
- Frontend: TG-groups nav-button показан для всех management (был admin-only)

**Management-write расширено до pm/vp/director:**
- All roster mutations (POST/PATCH/archive/restore), но не DELETE
- Materials create/update, project_materials add/patch
- Project create/update/archive/restore/complete
- `PATCH /api/users/{uid}/role` (set_user_role) — назначать роли может management
- Отчёты: править чужие, hours override, удалять чужие фотки
- Геофенс: обойти check-in radius, force-checkout, править radius

**Why:** Артём запросил "полный доступ ко всем возможностям OnTime кроме удаления проектов и прочего" для директоров, VP of construction и PM, 2026-04-21. Удаление осталось у admin, чтобы не потерять данные по ошибке не-admin'а.

**REVISION_AUTHOR_ROLES (расширено 2026-05-04):**
- Раньше: `{'estimator', 'director_estimator', 'admin'}` — только sm-роли могли создавать blueprint revisions.
- Теперь: + `pm/vp_construction/director` — management-роли могут грузить blueprints в проект (Mike Kripak / другие PM получали 403 на upload). Они и так в approval chain, авторство было единственным gap'ом.

**director_estimator vs director (gotcha):**
- При регистрации можно выбрать `director_estimator` (узкая office роль для blueprint review) — у неё management visibility, но НЕТ finance access (require_finance не включает её) → не видит Timesheet/Payroll. Если человек реально директор компании — поменять role на `director`. Ihor Marchenko (id=91) залетел как director_estimator 2026-05-04.
- 2026-05-06: `director_estimator` добавлен в `LIFT_MANAGER_ROLES`, `DELIVERY_CREATOR_ROLES`, `DELIVERY_WATCHER_ROLES`, `MANAGEMENT_ROLES` (бэк), `LIFT_MANAGER`+`DELIVERY_CREATOR` (фронт). Артём попросил "estimating director'у тоже полный доступ".
- **Finance access у director_estimator НЕ включён** — `require_finance` всё ещё пропускает только admin/accountant/pm/vp_construction/director/purchasing_manager. Если нужен Timesheet/Payroll для director_estimator — надо отдельно добавить.

**How to apply:** Когда добавляешь новый capability-gate:
- Backend: `require_management` на route + `_is_management(user)` в inline проверках — не `== 'admin'`.
- Frontend: `isManagement(me)` для edit/create/approve; `isAdminStrict(me)` только для destructive buttons (delete project, undo-complete, admin invite code).
- Новый DELETE endpoint? → admin-only (`require_admin`).
