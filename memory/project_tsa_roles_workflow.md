---
name: OnTime roles + notifications + Extra Work workflow
description: 4 новые управленческие роли, линейный approval workflow для Extra Work, persistent notifications с колокольчиком, director digest
type: project
originSessionId: 4513b864-6df3-4629-8b5d-c3e0f8273f0f
---
2026-04-20: добавлены 4 роли + notification center + расширенный EW workflow.

**Новые роли** (все self-register через invite code): `pm`, `vp_construction`, `director`, `purchasing_manager`. Инвайт-коды в `/root/ontime/backend/.env.bot` (TSA_PM_INVITE_CODE / TSA_VP_INVITE_CODE / TSA_DIRECTOR_INVITE_CODE / TSA_PURCHASING_INVITE_CODE). `MANAGEMENT_ROLES = {admin, pm, vp_construction, director}` — имеют finance_view, admin-read endpoints. `require_management` dependency для endpoints, которые должен видеть management chain.

**Extra Work линейный workflow:**
```
proposed → vp_approved → pm_approved → materials_ordered → done → invoiced → paid
            (VP)          (PM)          (Purchasing)       (any)    (Accounting) (Accounting)
```
Rejected — dead-end из любой стадии до `done`. VP/PM/Purchasing/Admin/primary foreman могут отклонить, причина опциональна.

**Audit trail:** таблица `extra_work_transitions(extra_work_id, from_status, to_status, actor_user_id, note, created_at)` — каждый переход пишется автоматически через `_record_ew_transition()`.

**Daily report integration:** eligible extras теперь только `status='materials_ordered'` (execution phase). Uncheck revert: `done`→`materials_ordered` (а не раньше).

**Notification Center:**
- Таблица `notifications(user_id, kind, priority, title, body, link_url, meta_json, created_at, read_at)`
- Endpoints: GET `/api/notifications`, `/api/notifications/unread-count`, POST `/api/notifications/{id}/read`, `/api/notifications/mark-all-read`, DELETE `/api/notifications/{id}`
- Helpers: `notify_with_store(conn, user_id, kind, title, body, link_url, priority, meta, tg_text)` — одновременно в DB + TG; `notify_role_with_store(conn, company_id, role, ...)` — для всех юзеров роли
- UI: `src/components/NotificationsBell.jsx` (колокольчик с red badge в header, polling каждые 30с, dropdown с deep-links), страница `/notifications`
- Deep-link EW: `/projects/{pid}?tab=extra&ew={eid}`. ProjectDetailPage читает `?tab=` из search params.

**Director digest:** cron 09:00 Calgary, считает extra_work_transitions за 24h GROUP BY status, шлёт TG+stored notification всем director+admin компании. Endpoint `/api/admin/director-digest/run` для ручного запуска. `_director_digest_loop` добавлен в `@app.on_event('startup')`.

**Why:** Артём описал реальный workflow TSA: foreman видит доп.работу → VP разрешает бюджет → PM финализирует → Purchasing заказывает → команда делает → Accountant выставляет invoice → admin/accountant отмечает оплаченным. Каждый получает нотификации по своей роли в цепочке.

**How to apply:** при расширении workflow (например + QA шаг после done) — добавь статус в `EXTRA_WORK_STATUSES`, endpoint-transition через `_ew_advance()`, notify_role_with_store к следующей роли, новый chip-цвет в `EW_STATUS_CHIP` frontend, i18n ключ `ew_status_<name>`. Скелет готовый.
