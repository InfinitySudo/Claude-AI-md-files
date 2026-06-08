---
name: project_tsa_oa_workflow
description: OnTime Order Acknowledgment (OA) workflow — vendor price/material confirmation against POs
metadata: 
  node_type: memory
  type: project
  originSessionId: 67a14daf-af74-4998-8c45-196c15d3320c
---

OnTime OA workflow (built 2026-06-02) — vendors confirm prices/materials for a PO we sent with empty/estimated prices.

**Flow:** PO emailed to vendor (subject already carries PO#, body asks for OA) → `oa_status='pending_oa'`. Vendor replies to `materials@threestonesalliance.ca` → IMAP sync links by PO# → `oa_received` → Claude parses doc → deterministic compare vs PO lines → clean=`oa_received` (awaiting human Confirm→`oa_verified`), differences=`oa_mismatch` + TG notify purchasing/director (PO held). Daily 09:00 Calgary re-request until OA arrives, max **5** then escalate.

**Code:**
- `backend/oa.py` — pure logic: `extract_po_numbers`, `extract_text_from_file` (pdftotext), `parse_oa_lines` (Claude), `compare_po_oa` (SKU + blended fuzzy name + exact price). Anthropic client reuses `TSA_ESTIMATOR_ANTHROPIC_KEY` (already in ontime-api env via .env.bot), OAuth fallback. NB: 2026-06-02 Артём явно велел переиспользовать эстиматорский ключ для OA — это ослабляет [[feedback_anthropic_key_scoped_estimator]] (тот запрет был про мою инициативу плодить ключи).
- `backend/main.py` — schema in `init_db` (tables `oa_emails`, `oa_email_attachments`, `po_acknowledgments`; PO cols `oa_status/oa_requests_sent/last_oa_request_at/oa_last_ack_id`); endpoints under `/api/oa/*` and `/api/purchase-orders/{id}/oa[/parse|/confirm|/apply-prices|/remind]`; background loops `_oa_parse_loop` (120s) + `_oa_resend_loop` (daily). OA request folded into existing `send_po_email`.
- `scripts/oa_imap_sync.py` — thin IMAP ingest (no Claude); systemd `oa-sync.service`+`oa-sync.timer` every 30 min. **Stores ONLY mail matching one of OUR OnTime POs that were actually emailed (`_match_po` → purchase_orders WHERE sent_at IS NOT NULL); все остальное (Kojo-доставки, рассылки, старые Kojo-PO MAGNA/ARABELLA/MG84) НЕ сохраняется.** Resume via `oa_sync_state.last_uid` high-water (set to current INBOX max on 2026-06-02 = 11335, so history isn't re-scanned — only new replies). materials@ INBOX ~11k general messages, so do NOT loosen the matched-only filter.
- Frontend: `src/components/OAInbox.jsx` (Procurement → "Materials / OA" tab), `OAPanel`+`OAStatusBadge` in `OrdersTab.jsx`, `oa.*`/`purchaseOrders.*OA*` in `api/client.js`. **Split PO↔OA compare view** (left=Our PO, right=Vendor OA, colour-coded match/price_diff/qty_diff/no_oa_price/missing_in_oa/extra_in_oa, verdict header). **Manual edit** of OA lines (edit desc/qty/price, add/delete, PO-ref chips) → confirmOA(id, lines, confirm): confirm=false = save & re-check, confirm=true = final verify. `compare_po_oa` flags price_diff ONLY when PO had a non-zero price (we send POs with $0).
- `confirmOA(confirm=true)` auto-applies vendor OA prices into PO line items + recomputes Subtotal/GST/Total (`_oa_apply_prices`); manual "Apply OA prices" button too.
- Overhead POs (no project) open a **PODetail modal in the Procurement queue** (PODetail exported from OrdersTab); project POs still navigate to the project Orders tab.
- PO email subject now includes project name; site contact (name+phone) auto-filled from project foreman on PO create.

**Live state (2026-06-02, commit 19fd1a0):** creds DONE — `materials@` is the same Google account as `ONTIME_SMTP_*` (in .env.bot), its 16-char app-password reused for IMAP in `backend/.env.materials`. **PO-2026-0001 (real)** = `pending_oa`, $0, awaiting Roofmart's OA (we emailed christine.ross@roofmart.ca). **PO-0000** = example/demo (overhead, invented materials+prices, OA with 2 price_diff) for showing the Purchasing Materials Director — delete later. po_counter reset so next real PO = PO-2026-0002. Related: [[project_tsa_procurement]], [[project_invoice_ingestion]], [[project_tsa_orders_queue_visibility]].
