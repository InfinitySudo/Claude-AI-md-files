---
name: Invoice OCR Followup (Tesseract)
description: One-shot systemd timer 2026-05-12 10:00 Calgary — Tesseract OCR re-parse over failed vendor_invoices, then canonicalize, TG report
type: project
originSessionId: c73850f7-e58a-4215-8ad9-bf032c1218be
---
**What:** Tesseract 5.3.4 installed on VPS. `pdf_to_text_ocr()` in `invoice_parser.py` — opt-in OCR fallback (3-8s/page) for scan-only PDFs (Hyatt, parts of Prime Fasteners, ABC, Sherwin, Kenroc).

**Files:**
- `/root/ontime/backend/invoice_parser.py` — `pdf_to_text(pdf_bytes, allow_ocr=False)` + `pdf_to_text_ocr()`
- `/root/ontime/scripts/ocr_followup.py` — walks `vendor_invoices` где `parsed_status='failed'`, OCR + fallback chain (primary parser → statement → generic), TG-отчёт админам
- `/root/ontime/scripts/ocr_followup.sh` — wrapper: invoice_imap_sync → backfill → ocr_followup → canonicalize_items
- `/etc/systemd/system/ocr-followup.{service,timer}` — one-shot `OnCalendar=2026-05-12 10:00:00 America/Edmonton`

**Why one-shot, не recurring:** OCR медленный + false-positive риск с loose-парсерами (`intuit_qb` ловит totals/taxes как items на OCR-text). Чейн `primary → statement → generic` снижает риск, но всё равно — лучше run once, посмотреть результат, потом решать.

**How to apply:** 
- Если timer не отстрелит — `systemctl start ocr-followup.service` руками.
- Логи: `journalctl -u ocr-followup.service -n 200`.
- Dry-run теста: `cd /root/ontime/backend && .venv/bin/python -c "import sys; sys.path.insert(0,'/root/ontime/scripts'); from ocr_followup import _best_parse; from invoice_parser import pdf_to_text_ocr; ..."`
- Если результаты норм после первого запуска — расширить timer до weekly или встроить OCR fallback прямо в `invoice_parse_backfill.py`.

**Known limits:**
- Hyatt OCR работает: ~5s/page, текст ~2300 chars, `parse_generic` поднимает 1 line item на типичный invoice.
- Очень короткие OCR (<800 chars) = битые сканы, остаются failed.
- `intuit_qb` исключён из chain именно для followup из-за false positives на не-QB OCR-тексте.
