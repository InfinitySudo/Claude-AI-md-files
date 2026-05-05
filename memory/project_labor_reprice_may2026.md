---
name: Labor Materials Reprice + Legacy Mapping (May 2026)
description: Полная цепочка reprice operations 2026-05-05 — pricing snapshot backfill + canonical mapping для archived legacy labor materials
type: project
originSessionId: 656b7c75-d454-4ed9-a10e-fd40c758b37e
---
2026-05-05 Артём попросил пересмотреть `unit_price_snapshot` в `daily_report_items` после того как зарплаты обновились и каталог получил STACK prices. Скоупом — отчёты с Jan-2026+ (раньше — закрытые периоды).

**Что сделано:**

1. **Backfill snapshot=catalog price** для labor materials, отчёты ≥ 2026-01-01. 325 rows updated, net delta −$362, 32 проекта.
2. **Mapping legacy → canonical** для 22 archived labor materials (high-confidence + exact-price):
   - Column→#438, L-girt→#505, Smart Panel→#472, Scratch-coat→#536, 3M→#571,
   - Corrugated→#477, Strapping 1"→#441, Hardie Panel+EZ→#459, Rainscreen→#535,
   - Thermal L Plate→#524, Butten&board→#481 (JH FC B&B Trim), Lux 6"→#484,
   - Artisan→#469, Stone→#522, VeneerBrick→#522, Chamclad→#448,
   - Trim 12"/Trim 2"→#474, 2 LayersOfPaper+Flashing→#563, 2 LayersOfBlackPaper+Flashing→#539,
   - Facsia (typo)→#498, Waterproofing→#525.
3. **Backfill snapshot из canonical price** для Jan-2026+ rows на этих 22. 2249 rows updated, net delta **+$56,728**, 32 projects (биггейст: Sage Walk Bldg 2 +$12k, Logel 3700 +$7.5k, MG84 Bldg 7 +$7.3k; биggest negatives: Magna Bldg 2 −$4.2k, Sage 600 −$4.2k).
4. **Создано 6 новых active labor materials** в каталоге:
   - #2291 Lux Soffit 4" - labor ($3.70 sf), #2292 Lux Soffit 6" - labor ($4.20 sf),
   - #2293 Labor - Stucco Finishcoat ($1.50 sf), #2294 Labor - Stucco Basecoat ($2.00 sf),
   - #2295 Thermal ISO Clips - labor ($3.50 ea), #2296 Shake - labor ($3.75 sf).
5. **Mapping legacy → новые canonical**: #63→#2291, #62→#2292, #14→#2293, #15→#2294, #10→#2295, #4→#2296, #34→#519 (Parging). Backfill этих — 1 row (#34 Pargin $5→$6); остальные snapshot уже совпадали с новой ценой.

**Skipped по решению Артёма:**
- #73 Brick (need disambiguation)
- #91 Pill&stick (непонятно что это)
- #82 Cated panels (used as helper-cut indicator, без цены)
- 4 active zero-price labor (#470 IMP, #471 Kingspan KarrierRail, #501 EZ trim, #557 Standard Mesh) — оставлены $0.

**Backups (полная цепочка отката):**
1. `/root/ontime/backend/tsa.db.bak-before-blueskin-split-20260505-162720` — pre-Sage 600 Blueskin redistribution
2. `tsa.db.bak-before-reprice-20260505-163120` — pre-первого global backfill
3. `tsa.db.bak-before-rollback-20260505-...` — pre-rollback (после первого global backfill, который потом откатили)
4. `tsa.db.bak-before-reprice-jan2026-20260505-...` — pre-Jan-2026-only backfill
5. `tsa.db.bak-before-canonical-20260505-170422` — pre-22 canonical mappings + backfill
6. `tsa.db.bak-before-newmats-20260505-...` — pre-6 new materials + 7 mappings

**Why:** prices в каталоге приехали из STACK позже чем многие отчёты были созданы → snapshot оказался stale. Archived legacy materials с короткими именами (типа "Blue Skin", "Stucco Basecoat") до сегодня не имели canonical mapping → их данные не катились в новую таксономию.

**How to apply:** Любой новый mass-edit prices начинай с backup. Schema: `materials.canonical_id` указывает на active material; `daily_report_items.unit_price_snapshot` frozen на момент создания. Чтобы пересчитать historical earned — UPDATE snapshot из canonical price только для конкретного date range. Не трогать pre-2026-01 (закрытые pay periods).
