---
name: estimator-assemblies
description: Multi-layer cladding stacks per takeoff — assembly_templates table + BOM разворот
metadata: 
  node_type: memory
  type: project
  originSessionId: a7860ae7-e5ec-4b08-a0dc-c01b073078ff
---

С 2026-05-25 в OnTime Estimator каждый wall/gable takeoff может ссылаться на **assembly_template** (multi-layer cladding stack) — типичная siding-сборка из 4-6 слоёв (cladding + wrb + insulation + strapping + fasteners + flashing).

**Schema** (`tsa.db`):
- `assembly_templates(id, company_id, key, label, description, default_for_system, layers_json)` — UNIQUE(company_id, key)
- `estimate_takeoffs.assembly_id` — FK на assembly_templates (nullable)

**layers_json** массив:
```json
[
  {"layer": "cladding", "material": "James Hardie HardiePanel HZ10",
   "category": "siding", "waste": 1.12, "unit": "sft"},
  {"layer": "strapping", "material": "1\" Z-girt GA18 24\" O/C",
   "category": "fasteners", "waste": 1.05, "unit": "lft", "ratio_to_area": 0.5},
  {"layer": "insulation", "material": "Cavity Rock 4\" mineral wool",
   "category": "insulation", "waste": 1.05, "unit": "sft"},
  {"layer": "wrb", "material": "Tyvek HomeWrap",
   "category": "insulation", "waste": 1.10, "unit": "sft"}
]
```

**ratio_to_area** = mультипликатор от area (1.0 default). Z-girts ставят на 24" O/C — это 0.5 LF/sft. Brick ties = 0.4 ea/sft.

**Seeded** (TSA company 1): hardie_panel_rainscreen_r21, hardie_lap_direct, lux_folded_wall, brick_cavity_r21, acm_rainscreen, vinyl_direct.

**BOM engine** (`_bom_for_estimate` в `main.py`):
- Для каждого takeoff с assembly_id — sum area по таким takeoff'ам, разворачиваем все layers в lines с `qty = covered × ratio × waste`, label `[assembly] material`.
- Не дублируем `siding` line если все walls под assemblies (используются их cladding layers).
- Global WRB/insulation rules продолжают работать для walls без assembly_id.

**Frontend:**
- `AssemblyTemplatesPage` (`/estimating/assemblies`) — CRUD с modal-editor, layers с up/down/delete.
- `SheetEditor` side panel: для selected wall/gable — Assembly dropdown.
- Кнопка **🧱 Assemblies** в `EstimatingPage` toolbar.

**Bot:** `list_assemblies()` + `get_assembly(id|key)` tools для @TSA_EstimatorBot.

**Why:** Sub Artem 2026-05-25 «нужно сделать многослойный Takeoffs, на одной картинке делать takeoffs для многослойного материала». Industry standard (Stack CT, PlanSwift) — assemblies dramatically точнее single-cladding-line подхода и переиспользуются.

**How to apply:**
- Новые стандартные сборки добавлять через UI на `/estimating/assemblies` или INSERT в DB напрямую.
- При импорте Excel BOM можно extract assembly из items (TODO: автоматический detector).
- Связано: [[project_estimator_links]], [[project_estimator_ai_memory]], [[project_estimating_industry_rules]].
