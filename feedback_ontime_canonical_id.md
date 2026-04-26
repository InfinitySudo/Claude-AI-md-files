---
name: OnTime materials.canonical_id alias chain
description: When labor catalog is replaced wholesale, old archived materials point to new canonical ones via canonical_id; installed_qty queries union both
type: feedback
originSessionId: 326669b3-b9b2-4025-a64a-317eeb368734
---
`materials.canonical_id` — указатель с OLD archived material на NEW canonical material того же смысла. Когда BOM проекта на NEW id, daily_report_items исторически на OLD id, нужно собирать installed_qty из обоих.

**Why:** 2026-04-25 заменили labor каталог (Stack import). Daily reports исторически писались на старые id 1-91 (archived), а BOM проектов 46/65 — на новые id 437+. Без alias UI показывал installed=0.

**How to apply:**
- Везде где собирается `installed_qty` из `daily_report_items` ПО material_id, использовать union:
  ```sql
  WHERE dri.material_id = m.id
     OR dri.material_id IN (SELECT id FROM materials WHERE canonical_id = m.id)
  ```
- Уже исправлено в: `project_materials_status` (line ~10215), `reorder_forecast` (line ~10160), budget endpoint (line ~3615), материалы проекта (line ~2340).
- Если добавляется новый endpoint с installed агрегацией — НЕ забыть alias union.
- Текущие mappings (на 2026-04-25):
  - 80 Blue Skin → 567 BLUESKIN VP160 + primer
  - 70 Insulation → 503 Labor 2-4" insulation
  - 72 Z Bars → 505 Z-girt
  - 87 Soffit → 548 Soffit Aluminum Royal
  - 88 Hardie Plank → 450 JH FC Lap Siding
  - 32 Hardie Panel No EZ → 459 JH FC Panel
  - 69 Trim 6" → 465 Half JH-Trm 5/4
  - 65 / 67 1 Layer*Paper+Flashing → 562 Tyvek 1 layer
  - 12 Folded Wall Lux → 478 Folded wall siding
  - 84 Metal Drips → 670 Custom flashing
  - 90 Trim 4" → 474 Smart Trim Prime~
- Не canonical: 3M (id 7), Stone (35), Strapping 3/8 (33), Lux Soffit 4" (63), Scratch-coat (38), Hardie Trim, Stucco* и др. — ждут уточнения от Артёма если понадобятся.
