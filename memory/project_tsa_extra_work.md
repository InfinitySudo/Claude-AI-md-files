---
name: OnTime Extra Work tab
description: Добавлена вкладка Extra Work с approval workflow, фото, TG-нотификациями и linkage в daily report
type: project
originSessionId: 4513b864-6df3-4629-8b5d-c3e0f8273f0f
---
В OnTime появилась 4-я вкладка на project detail: **Extra Work** (2026-04-20).

**Workflow:** proposed → approved/rejected → done → paid.
- Создать может любой на проекте (installer тоже — он на стройке первый видит).
- Approve/reject: admin + primary foreman + foreman_helper.
- Mark done: любой на проекте (когда status=approved).
- Mark paid: только admin.
- Цена (`price_usd`) скрыта от installer в listing, видна admin/foreman/accountant.
  Installer видит цену своей же записи (он её и ставил).

**БД:** `extra_work_items` + `extra_work_photos` (оба в init_db() `/root/ontime/backend/main.py`).
`report_id` связь с `daily_reports` — при отметке в форме daily report extra переходит done + линкуется.

**Intergations:**
- TG-нотификации: новая proposed → форман + админ; approve/reject → автору; mark-done → форманы.
- Daily report: чекбоксы approved extras в форме отчёта (ReportPage.jsx). Uncheck = revert to approved.
- Overview tab: строка "Extra Work: +$X (N approved · M pending)" открывает вкладку.

**Endpoints:** `/api/projects/{pid}/extra-work[/summary]`, `/api/extra-work/{eid}[/approve|reject|mark-done|mark-paid|photos[/{phid}]]`, `/api/reports/extras/eligible?project_id=...[&report_id=...]`.

**Reusable UI:** `/root/ontime/src/components/PhotoLightbox.jsx` — fullscreen swipe-галерея с touch/keyboard nav. Используется и в PhotosTab, и в ExtraWorkCard.

**Why:** Артём хотел учитывать работы за отдельную оплату (доп. софиты и т.п.), чтобы не терять деньги и иметь одобрение через админа до выполнения.

**How to apply:** при работе с финансами проекта всегда смотреть и часы-бюджет, и extra work committed sum. Цены хранятся как REAL USD (не cents) — так же как `projects.budget_usd`.
