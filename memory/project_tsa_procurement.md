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

## Catalog (added 2026-04-24)
- `vendor_materials` table: per-vendor offer (price, unit, pack, lead_time_days,
  availability, min_order_qty, vendor_sku, source, notes)
- Endpoints: `/api/materials/{id}/offers`, `/api/vendors/{id}/offers`,
  `POST/PATCH/DELETE /api/vendor-materials`, `/api/materials/catalog`
  (filters: q, category, available=in_stock|any, max_price, max_lead, vendor_id)
- UI tab "Catalog" in /procurement, OffersEditor modal per material
- PO form auto-fills unit_price from best offer once vendor+material chosen

## Calgary vendor directory (seeded 2026-04-24)
- 36 real local suppliers loaded into `vendors` table via
  `scripts/seed_calgary_vendors.py /tmp/calgary_vendors.json`
- Mix: 19 siding (Convoy/Gentek/Kaycan/Mitten/Royal/Star/Dicks/Mountain View/
  Taiga/Windsor×2/Home Depot×2/RONA+×2/Home Hardware×2/Roofmart is tagged
  'roofing'), 6 fasteners (Bolt Supply×3/Calfast×2/Grainger), 4 stucco
  (Target/Crown/Kenroc×2), 2 flashings (Regal/All Weather), 2 masonry
  (Brock White/I-XL), 2 rentals (Sunbelt/United), 2 roofing (Roofmart×2),
  1 sealants (Cloverdale)
- Seed script uses POST /api/vendors/bulk (admin-only, upsert by lower(name))
- Research done by background agent via WebSearch (no WebFetch access),
  emails only where publicly advertised

## Catalog bulk-fed from invoices (2026-05-04)
Артём решил: Catalog — единый прайс-лист по всем vendors, не curated.
Шаги выполнены:
1. `scripts/catalog/bulk_import_from_invoices.py --apply` →
   1618 новых materials + 1746 vendor_materials offers (`source='invoice'`).
   Group by SKU, regex чистка хвостов ("9 9 0 SKU 10.90 98.10").
2. `scripts/catalog/auto_categorize.py --apply --overwrite` → keyword rules
   (siding/trims/fasteners/sealants/underlayment/insulation/paint/masonry/
   stucco/tools/rentals/eavestrough/flashing/accessories/fees).
   `category='fees'` (632 шт) + delivery/statement junk → archived=1.
   359 unkategoryzowanych → category='other'. Покрытие 100%.
3. `scripts/catalog/auto_canonical.py --apply` → 8 групп склеилось через
   `canonical_id` (consервативный normalize по name). Кросс-vendor merge
   слабый без LLM, остальное руками.
4. UI: `/api/materials/category-counts` endpoint + dropdown показывает
   "trims (227)" с реальными counts. Expandable rows в Catalog table:
   клик на row → fetch + inline таблица vendor offers (sorted by price,
   cheapest зелёным).

Память не помнить значения counts — они меняются с каждым новым invoice;
читать через categoryCounts API. Cron weekly для refresh цен ещё не сделан
(deferred).

## Invoice catalog promote-on-demand (2026-05-04)
- Foreman in PO form has "From invoices" button → opens `InvoiceCatalogPicker`
  modal with search across `invoice_items` (filtered to PO vendor if picked).
- Each row: `Add` (one-off line, no Catalog row) or `Promote & add` (creates
  `materials` row + `vendor_materials` offer with `source='invoice'`, then
  adds line with `material_id`).
- Backend: `GET /api/invoice-items/search?q=&vendor_id=&limit=` aggregated by
  (vendor, sku|description), one row per SKU with last unit_price + n_purchases.
- Backend: `POST /api/invoice-items/promote` upserts material by case-insensitive
  name + vendor_materials offer (unique vendor+material).
- Why: vendor_invoices has 1100+ invoices / 3000+ SKUs, but Catalog stays
  curated. Foreman pulls from invoice history when curated catalog lacks an
  item; promotes only what they actually need.
- Vendor mismatch confirm: if picker item is from different vendor than PO,
  asks foreman to switch vendor on this PO.

## Deferred (future phases)
- Real SMTP email send (currently mailto: only)
- QuickBooks Online bill sync on status `received` → `paid`
- Bulk request (select multiple low materials → one PO per vendor)
- RFQ workflow (get 3 quotes, compare, convert winner to PO)
- Price learning: update materials.price from vendor invoice amounts
- Materials.category backfill: existing 91 materials have no category yet,
  so the catalog `category` filter is empty until someone tags them
