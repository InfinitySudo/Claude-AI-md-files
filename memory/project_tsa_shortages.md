---
name: OnTime Delivery Shortages
description: Shortage tracking on PO line items — Foreman flow for short-shipped deliveries with wait/reorder/resolved actions
type: project
originSessionId: 326669b3-b9b2-4025-a64a-317eeb368734
---
**Date:** 2026-04-25 (MVP shipped)

**Schema** — `purchase_order_items` extended:
- `shortage_qty REAL DEFAULT 0` — qty short-shipped
- `shortage_reason TEXT` — `out_of_stock` | `damaged` | `cancelled_by_vendor` | `wrong_item` | `other`
- `shortage_action TEXT` — `wait` (waiting same vendor restock) | `reorder` (foreman flagged for new PO) | `resolved`
- `shortage_created_at TEXT` — when shortage was first opened
- `shortage_resolved_at TEXT` — set when action='resolved'

**Why:** Foreman перепроверяет доставку, если приехало не всё — фиксирует short qty и решает: ждать того же вендора или перезаказать у другого.

**How to apply:**
- Receive endpoint (`POST /api/purchase-orders/{po_id}/receive`): `POReceiveLine` принимает optional `shortage_qty`/`reason`/`action`. PO считается `received` когда `qty_received + shortage_qty >= qty` для всех строк (shortage отслеживается отдельно, PO не блокируется).
- `GET /api/projects/{pid}/shortages` — открытые shortages (action wait/reorder, не resolved).
- `PATCH /api/po-items/{item_id}/shortage` — переключить action или закрыть.
- В `/api/projects/{pid}/materials/status` колонка pending = qty - qty_received - shortage_qty (только то что вендор реально привезёт). Дополнительно: `backlog_wait`, `backlog_reorder`. Needed = plan - installed - on_hand - pending - backlog_wait (reorder НЕ вычитается — нужно создать новый PO).
- Frontend Receive modal в `PODetail`: дополнительные колонки Short / Reason / Action в режиме receive.
- `ShortagesPanel` в OrdersTab: список открытых, кнопки Flag reorder / Wait / New PO (prefill) / Resolved.
- Daily TG nudge (piggyback на `_daily_report_nudge_loop`): shortages с action='wait' старше 7 дней → форману+админу: "пора reorder?".

**Trap:** при создании нового PO для перезаказа существующая shortage НЕ закрывается автоматически — Foreman должен явно нажать Resolved (или подтвердить при receive нового PO). Подумать про авто-резолв если очень нужно.
