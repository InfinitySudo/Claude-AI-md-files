---
name: OnTime Estimating Module
description: AI-assisted siding takeoff tab — Phase 1 (upload+render) shipped 2026-05-04, Phase 2-3 pending real PDFs
type: project
originSessionId: caee81af-88d6-4f38-9e35-a9e3b71df54e
---
Цель: счёт материалов из blueprint PDFs с точностью ±2% для PO к Roofmart. Объём 8-10 estimate'ов/нед.

**Архитектурное решение (важно!)**: чистый AI vision НЕ даст ±2%, так что путь — human traces walls на canvas, AI только ассистирует (auto-scale, классификация sheet'ов, BOM из catalog). Та же модель что invoice Inbox: AI набрасывает → человек подтверждает.

**Что есть (Phase 1, 2026-05-04):**
- Tab `/estimating` + `/estimating/:id`; виден management roles + 'estimator' (см. `canViewEstimating` в `src/lib/roles.js`, mirror backend `ESTIMATOR_VIEW_ROLES`)
- Tables: `estimate_projects` (job header, status: draft/takeoff/priced/sent/won/lost), `estimate_blueprints` (uploaded PDF), `estimate_sheets` (rendered PNG per page) — все в `init_db` `main.py:~1140`
- Endpoints `/api/estimates` (GET/POST/PATCH), `/api/estimates/{id}/blueprints` (POST upload, DELETE) с `require_estimator` gate
- PyMuPDF (pymupdf 1.27) рендерит PDF → PNG 150dpi, downscale для листов >36"; флаг `is_vector` = есть selectable text на первых 5 стр (определяет можно ли auto-extract позже)
- Frontend: список с status chips, detail с upload progress (XHR), thumbnail grid, click-to-zoom
- Хранилище: `/root/ontime/backend/uploads/estimates/{eid}/`, путь `/uploads/estimates/{eid}/{uuid}.pdf|.png`
- nginx (`/etc/nginx/sites-enabled/ontime`): отдельный location `~ ^/api/estimates(/|$)` с `client_max_body_size 250M` + 600s timeouts; общий `/api/` остался 25M. Nginx НЕ в гите — при ребилде сервера восстановить руками.
- Upload-first endpoint `POST /api/estimates/from-pdf` парсит title-block (regex на postal code + street types + cladding keywords + PROJECT:/RESIDENCE) и создаёт estimate в одном вызове; fallback на filename если ничего не нашлось

**Что добавлено 2026-05-04 в Phase 2-3:**
- Tracing canvas: HTML5 canvas (без Fabric.js — overkill); pan/zoom + 2-point calibration → px_per_ft persisted per sheet (memory: per-sheet not per-estimate, потому что site/floor/elevation разные scale)
- Polygon (closed=area) и polyline (open=LF) tools; kind enum: wall/gable/soffit/opening (additive/subtractive areas) + fascia/eave/corner_outside/corner_inside/drip_edge/starter/trim_band (linear)
- Tables: estimate_takeoffs (polygon_json + computed area_sqft + perimeter_lf, recompute on px_per_ft change), `parent_id` для opening→wall привязки
- BOM engine `_bom_for_estimate`: industry rules (Hardie waste 1.12, vinyl 1.08, Lux 1.10, mixed 1.12); WRB по ABC 9.36 = wall_area × 1.10; J-trim = ΣLF openings × 1.05; starter = traced или wall_perim/2 fallback × 1.05; corners = ⌈LF/12ft⌉; fascia × 1.10; soffit area × 1.10
- Catalog mapping `_catalog_candidates`: HARD unit filter (rl≠sft чтобы не считать Tyvek roll как sft); JOIN vendors; ДВА независимых match'а — purchase (на PO) и labor (install rate); НИКОГДА не смешивать — Артём специально подчеркнул

**Step 5b/5c/6 готовы 2026-05-04 (то же число, big push):**
- `coverage_per_unit + coverage_unit` columns on materials → BOM конвертирует "1 рулон Tyvek = 900 sft" автоматически: 1650 sft → ⌈1650/900⌉ = 2 rl × $110 = $220. Seed применён к Tyvek (900), Hal-Tex (400), Blueskin SA (225), JH-Trm 12ft pieces (12 lft).
- `estimate_bom_overrides` table + PUT /api/estimates/{eid}/bom-overrides → estimator может pin'нуть конкретный SKU из top-5 candidates для любой BOM line. UI dropdown в BOM panel: "change ▾" → выбор → 📌 indicator. Override переживает recalc.
- POST /api/estimates/{eid}/draft-pos → создаёт draft purchase_orders сгруппированные по vendor через existing procurement flow (po_number seq, transitions, 5% tax). Coverage candidates заказываются целыми единицами (rolls/boxes), не sft. Lines без price/vendor skip'аются с reason'ом.

**Что НЕ сделано:**
- Vector-PDF auto-extraction геометрии (если PDF vector — пропустить человеческую трассировку линий)
- Claude Vision для классификации sheet типов (Артём отказался — feedback_estimating_no_api)
- Hardie Plank/Panel purchase items в catalog — нет в DB, поэтому BOM показывает "no match" для cladding lines; нужно либо добавить руками, либо подтянуть с invoice'ов
- BOM по-vendor breakdown summary (видно через draft PO list, но не в самой BOM panel)

**Why:** Артём попросил начать с tab'а чтобы загрузить примеры PDFs; формат blueprints (vector vs scan) определяет приоритет Phase 2 vs Phase 3.

**How to apply:** При следующих итерациях — сначала посмотреть какие PDF Артём загрузил (`SELECT * FROM estimate_blueprints`), их `is_vector` и `page_count`. Если 80%+ vector → Phase 3 (auto-extract) даёт максимум value. Если scan-only → Phase 2 (tracing UI) обязателен. Tracing data добавится новыми таблицами `estimate_takeoffs` + `estimate_takeoff_lines`, не трогая существующие.

**Critical mental model для будущих коммитов:**
- materials.kind='purchase' = caталог Roofmart/других vendor'ов (closing material cost для PO)
- materials.kind='labor' = TSA внутренние install rates ($/sft за работу установщика)
- Это РАЗНЫЕ деньги. Никогда не суммировать в одну колонку. BOM показывает их отдельно: material_total (PO) и labor_total (install).
- В catalog'е цены от ВСЕХ vendor'ов: Roofmart Calgary North/South (id 8/9), Convoy, Gentek, Kaycan, Brock White, I-XL и т.д. — Roofmart это primary но не единственный. Step 6 (draft PO) должен либо позволить выбрать vendor, либо группировать строки по vendor'у в multiple PO.
- Hard unit compatibility (sft↔sf, lft↔lf, pc↔ea) обязателен — иначе Tyvek roll $134 × 1650 sft = phantom $221k (исправлено 2026-05-04)
