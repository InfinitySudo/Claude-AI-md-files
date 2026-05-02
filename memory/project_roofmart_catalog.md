---
name: Roofmart Catalog Sync
description: Working pipeline to scrape Roofmart ProZone invoices and import line items as priced materials. 92 SKUs imported 2026-04-24 covering 63/70 invoices.
type: project
originSessionId: 4d4d919f-6dfb-44a4-bbcd-6bbe738df432
---
**Что есть в проде (2026-04-24):**

OnTime catalog содержит **92 уникальных Roofmart SKU** с актуальными ценами март-апрель 2026:
- vendor_materials.vendor_id=8 = Roofmart Calgary South
- Источник: 63 invoices через ProZone
- $241k spend coverage

**Pipeline (`/root/ontime/scripts/`):**
1. `roofmart_export_all.py` — Playwright headed (xvfb) → ProZone CLOSED tab → Export All → CSV (70 invoices summary)
2. `roofmart_full.py` — для каждого invoice: `loc.click(force=True)` → wait popup → собирает SF IDs → fetch PDFs через `context.request.get(apex_url)`
3. `roofmart_import_all.py` — pdfplumber парсит каждый PDF → upsert materials + vendor_materials. Match by SKU first, then name+unit.
4. `dedup_materials.py` — мерджит materials с одинаковым SKU
5. `roofmart_weekly.sh` — обёртка для cron, запускает 1-4

**Cron:** `roofmart-weekly.timer` (systemd) — каждое воскресенье 03:00 Calgary.

**Известные ограничения:**
- 7 из 70 invoices пропущены (NO_POPUP в loop). Salesforce видимо bot-detect'ит сессию после ~50 кликов и перестаёт открывать popups. Triple-click не помог.
- Mapping в `_mapping.json` содержит **offset-by-1** в attribution — popup от click N приходит во время click N+1's wait window. Но **content PDF корректный** (filename invoice# wrong, but the PDF itself is the right one for the URL). Парсер берёт invoice# из контента → catalog корректный.

**Roofmart PDF parser (in `main.py`):**
- `_RM_HEADER_RE` — `qord qshp qrem UOM SKU` строка
- `_RM_TOTAL_RE` — `UOM unit_price ext_price` строка
- `_RM_COMBINED_RE` — однострочный layout (header+total склеены)
- Поддерживает credit memos с negative qty (`- 3 - 3 0 PC ESTD45DWG`)
- Multi-page dedup по `(sku, qty, ext)` сигнатуре
- `_is_boilerplate()` обрезает description при встрече SUB-TOTAL/GST/Page/REPRINT/etc.

**How to apply:**
- Если Артём спрашивает «обнови catalog» — `systemctl start roofmart-weekly.service` запустит вручную
- Если хочется добавить второй vendor (Convoy, Kenroc) — клонировать pipeline, vendor_id меняется в import_all
- Catalog UI: `/procurement` → tab Catalog с фильтрами по vendor/category/price/lead_time
