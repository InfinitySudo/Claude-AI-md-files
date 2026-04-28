---
name: Billable service tasks workflow
description: Billable service tasks must transit service → to_invoice → (accounting) → complete; service role cannot skip to complete
type: feedback
originSessionId: c73850f7-e58a-4215-8ad9-bf032c1218be
---
**Rule:** When a service task has `service_type='billable'`, the close button is locked away from the `service` role. They can only push it to `to_invoice`. Only management (admin/accountant/pm/vp_construction/director) can mark it `complete`, and only after `service_invoice_no` is recorded.

**Why:** 2026-04-28 — Andrei (service) finished "Fix the trim" on a billable callback and clicked Complete. The task moved straight to "Complete" column, accounting never saw it, no invoice was issued. Артём: «esli ya pri sozdanii zadachi ukazivau bileble service otchet doljen idti po naznacheniu ne zavisimo ot togo chto najal servise guy».

**How to apply:**
- Backend `patch_service_task` (main.py): if `service_type='billable'` and new `status='complete'`:
  - non-`_can_close_billable` (everyone except admin/pm/vp/director/accountant) → silently rewrite to `to_invoice`
  - `_can_close_billable` without `service_invoice_no` → HTTP 400 with explanation
- Helpers (main.py): `_can_view_all_service` (board readers) and `_can_close_billable` (closers). Accountant is included in both.
- On transition `* → to_invoice` for billable, broadcast TG to admin+accountant+pm+vp_construction+director via `_notify_billing_team()` so accounting picks it up. The TG message auto-includes a "🔗 Open in app" inline-keyboard URL because `notify_with_store` adds it for any in-app link_url.
- Frontend `ServicePage.jsx`: filter `complete` option out of the status dropdown when `service_type==='billable'` and current user is not in `['admin','accountant','pm','vp_construction','director']`; show purple banner inside the task modal explaining the workflow. ServicePage reads `?open=<id>` from the URL to deep-link from TG.
- i18n keys: `svc_billable_banner` (en/ru).
- Existing tasks closed incorrectly: revert via SQL — `UPDATE service_tasks SET status='to_invoice', completed_at=NULL WHERE id=...`. Always check `service_type='billable'` before reverting.
