---
name: OnTime roles + access matrix
description: Management (pm/vp_construction/director) получают admin-equivalent capability во всём, кроме destructive и invite-code governance
type: project
originSessionId: f1c65322-19fe-4461-86eb-62acb1eaf226
---
OnTime роль-хелперы и матрица доступа — как расширялось в 2026-04-21.

**Backend helpers (`ontime/backend/main.py`):**
- `MANAGEMENT_ROLES = {'admin', 'pm', 'vp_construction', 'director'}` (~line 70).
- `require_management` (Depends) — для не-destructive mutation endpoints. Строго возвращает 403 для всех остальных.
- `_is_management(user)` — inline capability check. Использовать вместо `user['role'] == 'admin'` в capability-тестах (edit report, approve extras, override geofence, delete чужого фото и т.д.).
- `require_admin_or_accountant` — read access: admin/accountant/pm/vp/director (+не мутации). Accountant тоже здесь.
- `_has_finance_view(user)` — видит ли $-колонки: admin/accountant/pm/vp/director/purchasing_manager.

**Frontend helpers (`ontime/src/lib/roles.js`):**
- `isManagement(me)` — для UI gates: редактировать/создавать/аппрувить/override.
- `hasFinanceView(me)` — показать ли $-поля.
- `isAdminStrict(me)` — для destructive/governance кнопок (см. ниже).

**Admin-only (оставлено, НЕ расширено):**
- `DELETE /api/projects/{pid}` (удалить проект — явно сказано Артёмом нельзя)
- `DELETE /api/roster/{rid}`
- `DELETE /api/materials/{mid}`
- `DELETE /api/projects/{pid}/materials/{mid}`
- `POST /api/projects/{pid}/undo-complete` (реверсирует scoring/badges)
- `POST /api/cron/director-digest/run` и `/daily-report-nudge/run` (cron runners)

**Management-write расширено до pm/vp/director:**
- All roster mutations (POST/PATCH/archive/restore), но не DELETE
- Materials create/update, project_materials add/patch
- Project create/update/archive/restore/complete
- `PATCH /api/users/{uid}/role` (set_user_role) — назначать роли может management
- Отчёты: править чужие, hours override, удалять чужие фотки
- Геофенс: обойти check-in radius, force-checkout, править radius

**Why:** Артём запросил "полный доступ ко всем возможностям OnTime кроме удаления проектов и прочего" для директоров, VP of construction и PM, 2026-04-21. Удаление осталось у admin, чтобы не потерять данные по ошибке не-admin'а.

**How to apply:** Когда добавляешь новый capability-gate:
- Backend: `require_management` на route + `_is_management(user)` в inline проверках — не `== 'admin'`.
- Frontend: `isManagement(me)` для edit/create/approve; `isAdminStrict(me)` только для destructive buttons (delete project, undo-complete, admin invite code).
- Новый DELETE endpoint? → admin-only (`require_admin`).
