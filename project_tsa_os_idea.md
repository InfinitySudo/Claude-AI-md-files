---
name: TSA OS — Unified Company Platform (active)
description: Reactivated 2026-04-24. OnTime becomes the single app for TSA — replacing Kojo (procurement) AND ClickUp (tasks/docs/CRM). Was paused 2026-04-16, now resumed with stricter scope (no more "keep Kojo as satellite").
type: project
originSessionId: d17635cc-9fb8-4333-ba35-356494af8a39
---

**Статус:** Активна с 2026-04-24. Артём: «хочу убрать Kojo, ClickUp из компании, хочу пользоваться только OnTime app для всех нужд».

**Изменение стратегии vs 2026-04-16:**
- Было «Hub + connectors, Kojo остаётся сателлитом» → стало **«OnTime ест всё»**. Kojo выключаем полностью, не интегрируем.
- ClickUp всё так же выключаем.
- STACK (estimating) — не обсуждался в этой сессии, статус неизвестен, вероятно тоже на выход.

**Что уже есть в OnTime (проверено 2026-04-24):**
- Projects, Daily reports, Extra Work, Deliveries, Lifts/Refuels, Heartbeat/time-tracking
- Procurement schema: `vendors`, `purchase_orders` (с 3-tier approval draft→purchasing→pm→director→approved→sent→received→paid), `purchase_order_items`, `vendor_materials`, `materials`
- PO PDF generator через reportlab (80% Kojo parity — не хватает SENT BY/Required Time/Ship Via/Discount/Shipping)
- Vendor directory v1 (30 Calgary suppliers с categories/brands/quadrant/flags)
- Roles matrix: admin, pm, vp_construction, director, foreman, purchasing_manager, service_manager, delivery_manager
- TG bot + web push

**Что ещё нужно для полноценной замены (Kojo + ClickUp):**
1. **PO PDF parity с Kojo** — SENT BY, Required Time, Ship Via, Delivery/Additional Notes, Discount/Shipping линии. ~30 мин.
2. **Invoice PDF importer** — drag-and-drop Roofmart invoice → парсит line items → upsert в vendor_materials с ценой и датой. ~1 час. Альтернатива Salesforce скрейпингу.
3. **Materials catalog UI** — в /procurement tab Catalog уже есть, дописать add-material + vendor offers binding. ~1 час.
4. **Generic tasks** — то, что ClickUp даёт: свободные задачи с assignee/due/status/comments/attachments, не привязанные к project или daily-report. Новая таблица `tasks`, UI как Kanban + list. Это новая большая фича.
5. **Docs space** — как ClickUp Docs. Простой wiki/notes (Markdown), folder-structure, attachments. Большая фича.
6. **Automations** — триггеры «when X happens → do Y». Можно отложить.

**How to apply:**
- Любая фича, обсуждавшаяся раньше в контексте Kojo/ClickUp, теперь делается внутри OnTime, не интегрируется снаружи.
- Перед большими фичами (tasks, docs) уточнять у Артёма приоритет — эти две огромные.
- PO/Procurement/Invoice — приоритетная полоса сейчас.
- Roofmart Salesforce-скрейпинг — deferred. Салесфорс iframe+popup ад, лучше через PDF-импорт.

**Прошлые открытые вопросы (пересмотреть):**
1. Django admin доступ — не упоминался 2026-04-24, статус ?
2. STACK API — не упоминался 2026-04-24.
3. Kojo API — **не нужен**, выключаем Kojo.
4. Payroll module — не упоминался 2026-04-24.
