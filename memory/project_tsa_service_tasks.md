---
name: OnTime Service Tasks (Andrei Mesca's tab)
description: QA + warranty + standalone service ticket flow with kanban + checklist + categorized photos
type: project
originSessionId: 326669b3-b9b2-4025-a64a-317eeb368734
---
**Date:** 2026-04-25 (MVP shipped)

**Role:** новая `service` role (`_position_to_role` 'service' → 'service'); добавлена в NON_ROSTER_ROLES (Andrei = office-style, не на roster). Invite code `TSA_SERVICE_INVITE_CODE` уже был в `.env.bot` = `Service-2026-MI5A`.

**Tables:**
- `service_tasks`: title, description, project_id (NULLABLE — standalone OK), assignee_id, status, service_type, address (для standalone), warranty_end_date, service_invoice_no, service_work_hours, tenant/responsible name+phone, weather, review_date_time
- `service_task_checklist`: 11 default items auto-seeded в `_seed_service_checklist`. Toggle через `POST /service-tasks/{tid}/checklist/{cid}/toggle`
- `service_task_photos`: category enum (`before|during|after|materials_po|progress|estimation`); файлы под `/uploads/service_tasks/{tid}/`
- `service_task_comments` — body + `mentioned_user_ids` (CSV user_ids; добавлено 2026-04-30)

**Statuses (kanban):** `to_do → acknowledged → in_progress → to_invoice → complete`

**Endpoints:** `/api/service-tasks` (list/create/get/patch/delete) + child mutations + `/service-installers` (для assignee picker) + `/service-tasks/{tid}/mentionable` (для @-picker по ролям).

**Visibility (2026-04-30):** `_is_service` = role IN (service, delivery) OR management. Delivery теперь полноправный участник service flow — может создавать, видеть kanban, быть в picker assignee, менять статусы/checklist/photos/комменты. Билинг (close billable → complete) остаётся за management+accountant. Не-service+delivery видят только свои assigned tasks.

**Frontend:**
- `/service` page (кнопка Wrench в верхнем меню видна для service/admin/director/pm/vp).
- Kanban из 5 колонок с TaskCard.
- Detail modal: inline edit title/description, status dropdown, expandable Service fields, checklist, photos by category (с upload), comments.

**Регистрация Andrei Mesca:**
1. Открывает app → `Sign up`
2. Position = `Service`
3. Invite code = `Service-2026-MI5A`
4. После регистрации появляется в `/service-installers` как assignee.

**Notifications (готово 2026-04-30):**
- Создание/реассайн task → `_notify_service_assignee` → bell + TG + push
- Комментарий БЕЗ @-mentions → fallback на assignee+creator, kind=`service_task_comment`, priority=info
- Комментарий С @-mentions → ТОЛЬКО упомянутым, kind=`service_task_mention`, priority=action_required
- UI: кнопка `@` рядом с input разворачивает picker с группировкой по ролям (multi-select chips)
- Silent `except Exception: pass` в notify-путях заменён на `print(...)` — провалы видны в `journalctl -u ontime-api`
- Web push требует чтобы юзер один раз подписался через PWA (Андрей пока не подписан, у него только bell + TG)

**Что НЕ сделано (если понадобится):**
- Auto-create QA task когда project достигает 85-90% installed (Артём упомянул как идею).
- Activity log (showing who changed what when).
- Subtasks (Артём явно сказал — не нужно, только checklist).
