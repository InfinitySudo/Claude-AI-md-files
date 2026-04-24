---
name: OnTime Procurement
description: Vendors + Purchase Orders MVP added to OnTime 2026-04-24. Tiered approval by total, foreman self-serve below T1. Kojo replacement.
type: project
originSessionId: 0b7f8333-e4e6-449e-ab4e-87bc4bf444fc
---
Artem decided **not** to clone Kojo. Instead, procurement lives inside OnTime
alongside projects/materials/budget. Shipped as Phase 1 on 2026-04-24.

**Why:** 10-15 recurring vendors, repeating SKUs, need connection to project
budget, need QBO bill export later, too much Kojo complexity is dead weight
for a Calgary siding company.

**How to apply:**
- Any procurement question → these are the tables/endpoints/roles to look at
  first, not a new integration.
- New PO workflow logic lives in `_compute_po_stages()` in backend/main.py
- Email send is mailto: only right now; real SMTP + QBO sync are phased for
  later.

## Schema (sqlite, backend/main.py)
- `vendors` — name, contact, email/phone/address, category, payment_terms, archived
- `purchase_orders` — po_number, vendor_id, project_id, status (10 states),
  subtotal/tax/total, needed_by, is_urgent, pdf_path, qbo_bill_id (unused yet)
- `purchase_order_items` — material_id, description, qty, unit, unit_price,
  line_total, qty_received
- `po_approvals` — one row per required stage (purchasing | pm | director)
- `po_transitions` — audit log of status changes
- `materials` extended: sku, category, default_vendor_id, reorder_threshold
- `companies` extended: legal_name, address, gst_number, gst_rate, po_prefix,
  po_counter, po_threshold_purchasing/pm/director, contact_email/phone

## Tiered approval (configurable per company)
- < T1 ($500 default) → auto-approved on submit
- T1..T2 ($2000 default) → purchasing only
- T2..T3 ($10000 default) → purchasing + PM
- ≥ T3 → purchasing + PM + director
- `is_urgent` flag skips PM for mid-range POs; director stage never skips.

## Roles
- Foreman: creates drafts, submits, receives
- `purchasing_manager` / director / admin: stage "purchasing" approve, can edit
  any draft/pending_purchasing PO, can cancel any active PO
- PM / vp_construction / director / admin: stage "pm"
- Director / admin: stage "director"
- Accountant + purchasing/director: log invoice/payment

## Key endpoints
- `/api/vendors` GET/POST, `/api/vendors/{id}` PATCH/DELETE(archive)
- `/api/procurement-settings` GET/PATCH
- `/api/purchase-orders` POST, `/api/purchase-orders/{id}` GET/PATCH
- `/api/purchase-orders/{id}/submit|decide|send|receive|invoice|cancel`
- `/api/purchase-orders/{id}/pdf` — reportlab + Range support
- `/api/projects/{pid}/purchase-orders` list per project
- `/api/projects/{pid}/materials/status` — foreman dashboard data:
  planned/delivered/installed/on_hand/pending/needed + needs_reorder flag

## UI surfaces
- Project page: new "Orders" tab (`OrdersTab.jsx`) — materials status +
  PO list + create/detail modals
- `/procurement` page (`ProcurementPage.jsx`) — Queue / Vendors / Settings tabs

## Deferred (future phases)
- Real SMTP email send (currently mailto: only)
- QuickBooks Online bill sync on status `received` → `paid`
- Bulk request (select multiple low materials → one PO per vendor)
- RFQ workflow (get 3 quotes, compare, convert winner to PO)
- Price learning: update materials.price from vendor invoice amounts
