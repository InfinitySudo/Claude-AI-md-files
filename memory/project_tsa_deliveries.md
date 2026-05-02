---
name: OnTime Deliveries (material delivery planner)
description: delivery-tasks модуль OnTime — workflow, роли, integration с Extra Work
type: project
originSessionId: 010f69fe-2832-4848-b976-a212173a4547
---
Shipped 2026-04-23 для delivery-роли (доставщик материалов). Раньше у delivery были только refuel sub-task + shift stops; теперь — полноценный планировщик доставок.

**БД (`/root/ontime/backend/tsa.db`):**
- `delivery_tasks` — статусы `pending → on_the_way → delivered`, `cancelled` из любой точки. Priority: `urgent|high|normal|low`. Foreign keys: `project_id`, `extra_work_id`, `assigned_to_user_id`, `created_by_user_id`.
- `delivery_task_items` — checklist с `picked_up`, `delivered` галочками
- `delivery_task_photos` — phase: `pickup|delivery|reference|other`

**Роли:**
- `DELIVERY_CREATOR_ROLES` = {admin, director, vp_construction, pm, purchasing_manager} — create/edit/cancel
- Драйверы = users с `roster.role IN ('delivery', 'service')`
- Driver видит только свои задачи; management видит всё

**Endpoints (`/api/delivery-tasks/*`):**
- CRUD + `/start`, `/complete`, `/cancel`, `/items/{iid}` toggle, `/photos`
- `/summary?date_from=&date_to=` → by_status, by_priority, per_driver, avg_created_to_delivered_min
- `/pending-from-ew` + `/api/extra-work/{eid}/delivery-prefill` — Extra Work → delivery flow
- `/api/me/delivery-tasks` — для драйвера, default today→+7

**TG/уведомления (встроены в endpoints):**
- create → driver + management watchers
- start/complete → creator + management + foreman проекта
- cancel → driver + management
- **Morning briefing 07:30 Calgary** (`run_driver_briefing`) — TG драйверу со списком на день

**UI:**
- `/deliveries` → `DeliveriesPage.jsx` — календарь по датам, фильтры, create/edit modal, pending-from-EW панель
- ShiftPage добавлен блок "Доставки на сегодня" с Start/Complete
- `canManageDeliveries(me)` + `isDriver(me)` в `lib/roles.js`

**Why:** Delivery работал вслепую — получал задачи устно, никто не видел статуса, материалы Extra Work приходилось заказывать и доставлять разными руками. Теперь Purchasing Manager создаёт доставку из EW одним кликом, driver получает TG-briefing в 07:30 и отмечает прогресс.

**How to apply:** При правке логики доставок — проверить все 4 роуты (`GET /api/delivery-tasks/pending-from-ew`, `summary`, `{did}`, `{did}/*`) — route order критичен, static сегменты должны быть ДО `{did}` из-за int-типа.
