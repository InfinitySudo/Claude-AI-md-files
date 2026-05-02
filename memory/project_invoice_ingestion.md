---
name: Invoice Ingestion Pipeline
description: OnTime invoice@threestonesalliance.ca IMAP → DB → Vendor Prices + Canonical Materials grid. 23 regex parsers, 2079/2945 invoices parsed (71%), $2.42M of $3M spend. Daily cron. Updated 2026-04-28.
type: project
originSessionId: fe2d774e-d849-434f-9578-413ba05df8a4
---
Цель: собрать максимальную базу материалов и цен от всех вендоров через парсинг ВСЕХ инвойсов из mailbox `invoice@threestonesalliance.ca`. Финальный UI — Procurement → Vendor Prices grid (per-vendor SKU + canonical cross-vendor). Артём 2026-04-28: «никаких API-ключей, только regex per-vendor parsers как для Roofmart».

**Why:** OnTime превращается в product; vendor price intelligence — конверсионный фичер для других siding-компаний.

**How to apply:** Pipeline идёт фазами. Не использовать Claude/OpenAI API (см. feedback_no_api_keys_invoice). Per-vendor template = `vendors.parser_template` → routing через `vendor_email_domains.domain → vendor_id → parser_template` → функция в `invoice_parser._TEMPLATE_PARSERS`.

## Готово (2026-04-28)

- **IMAP backfill** (2026-04-27): 8766 emails, 12055 attachments (4717 PDF), 8.5 GB в `/var/ontime/invoices/<uid>/`. Скрипт `/root/ontime/scripts/invoice_imap_sync.py` (idempotent UID-tracker).
- **Schema**: `invoice_emails`, `invoice_email_attachments`, `vendor_invoices` (UNIQUE (company_id, attachment_id)), `invoice_items` (FK ON DELETE CASCADE, +canonical_id), `invoice_item_aliases`, `vendor_email_domains` (domain → vendor_id), `canonical_materials` (cross-vendor), колонка `vendors.parser_template`.
- **Vendor seeding**: `scripts/seed_vendor_domains.py` — 41+ supplier domains → vendors, 81 non-vendor noise в deny-list.
- **23 vendor regex parsers** (раскиданы по нескольким файлам, см. диспетчер `_TEMPLATE_PARSERS` в `/root/ontime/backend/invoice_parser.py`):
  - `invoice_parser.py`: roofmart, wayne, whitecap, ixl, convoy, adss, tsdstone, primefasteners (scan-only, returns []), ccan, gentek, polimark, adex, sascaffold, monarch, generic
  - `vendor_parsers_extra.py`: cascadeaqua (custom font glyph map), calfast
  - `vendor_parsers_smallvol.py`: hyatt (scan-only), ecostone, baum, sherwin, cloverdale, kms, **intuit_qb** (QB passthrough — 3 layouts: ITEM/QTY/RATE/AMOUNT, DESCRIPTION/ITEM/AMOUNT с "N @ CAD X.YY", PRODUCT/SERVICE)
  - `vendor_statement_parser.py`: parse_statement — единый для jays/herc/kenroc/ant + fallback для whitecap statements
  - `vendor_parser_abc.py`: parse_abc + pdf_to_raw_text (использует `pdftotext -raw` с shadow-line decoder для bisTrack PDF)
- **Dispatcher fallback chain** в `parse_pdf_bytes()`: jays/herc/kenroc/ant → если parse_statement пустой, пробует parse_intuit_qb (QB passthrough invoice через jaysmetal.com); intuit_qb → если пустой, parse_statement; whitecap/прочие → если пустой, parse_statement.
- **Intuit QB routing**: в `scripts/invoice_parse_backfill.py::_resolve_vendor` домены `notification.intuit.com`, `intuit.com`, `quickbooks.intuit.com` → принудительно template='intuit_qb', vendor_id остаётся NULL.
- **Orchestrator**: `scripts/invoice_parse_backfill.py` — UPSERT по (company_id, attachment_id), `--template`, `--limit`, `--reparse`, `--dry-run`.
- **Daily cron**: `invoice-sync.timer` (systemd) → `invoice-sync.service` запускает IMAP sync + parser backfill каждый день в 03:00 Calgary. `journalctl -u invoice-sync` для логов.
- **Cross-vendor canonicalization**: `scripts/canonicalize_items.py` (rapidfuzz, threshold=85, token_set_ratio в пределах одной UoM-группы). Кластеризует 2021 уникальных (vendor×sku×uom×desc) → 709 canonical_materials. 5 cross-vendor групп (мало — потому что у вендоров разные форматы описаний даже для одинаковых товаров).
- **Backend endpoints** (main.py ~10690):
  - `/api/invoices/vendor-prices` — per-vendor agg с rollup banner
  - `/api/invoices/vendor-prices/{vid}/{sku}/history` — drill-down price history
  - `/api/invoices/canonical-prices` — canonical materials с per-vendor offers, best price highlighted
- **Frontend**: `src/components/VendorPricesGrid.jsx` — таб "Vendor Prices" в `/procurement` с двумя view-toggle: "Per-vendor SKU" (плоская таблица + drill modal) и "Canonical (cross-vendor)" (expandable cards с per-vendor offers, best price highlighted, CROSS-VENDOR badge на n_vendors≥2).
- **PDF text extraction**: `pdf_to_text()` использует pdfplumber, fallback на poppler `pdftotext -layout` для PDF с font encoding issues.

## Coverage snapshot 2026-04-28 (после полной интеграции)

- **parsed: 2079** invoices ($2.42M)
- **failed: 778** (parser отработал, 0 items — в основном scan-only PDF без OCR)
- **unmatched: 88** (3% — мусор + sender'ы без parser_template)
- **canonical_materials: 1172** items, **53 cross-vendor** (было 5)

Топ-парсеры по объёму:
intuit_qb 371 + jays_to_intuit_qb 52 + herc_to_intuit_qb 55 = 478 QB-passthrough invoices разобрано.
roofmart 326 / abc 235 / whitecap 173 / wayne 161 / convoy 95 / ccan 85 / tsdstone 83 / adss 72.
whitecap_to_statement 14, intuit_qb_to_statement 28 — fallback chain работает.

## TODO

- **Failed остатки = scan-PDF без OCR**: Hyatt 23, Prime Fasteners 97, Sherwin 13, Kenroc 21, ABC 53 (часть). Нужен Tesseract pre-pass — без AI API. Не приоритет, общий $ объём ~$300K.
- **Statement parser** для invoice headers (без line items): извлекать invoice_no + total + date из statements (Jay's, Kenroc, ANT) для cross-reference.
- **Boost cross-vendor matches**: strip brand/size/color from description before matching (53 → возможно 200+).
- **TG алерт на parse_failed** в cron-script.

## Restart cheatsheet

```bash
# Run cron job manually
systemctl start invoice-sync.service
journalctl -u invoice-sync -n 50

# Reparse single vendor
cd /root/ontime/backend && .venv/bin/python ../scripts/invoice_parse_backfill.py --template wayne --reparse

# Re-canonicalize after new data
cd /root/ontime/backend && .venv/bin/python ../scripts/canonicalize_items.py --threshold 85

# Check cron status
systemctl list-timers invoice-sync.timer
```
