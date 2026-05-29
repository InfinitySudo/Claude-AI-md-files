---
name: project-ai-trace-teach
description: "AI Trace учится по правильно обведённым sheet'ам. Артём (или эстиматор) обводит руками → кнопка «Teach AI» → пример сохраняется в ai_trace_examples → следующий AI Trace получает его в Sonnet prompt как few-shot reference."
metadata: 
  node_type: memory
  type: project
  originSessionId: a7c17f24-1434-4a2c-b45d-6a43248a8f2f
---

## Pipeline

1. **UI button «Teach AI»** в SheetEditorPage (рядом с «AI Trace» / «Clear AI»):
   - Активна когда на sheet есть >=1 takeoff
   - Просит optional notes («multi-elevation, не дробить ribbed»)
   - POST `/api/estimates/{eid}/sheets/{sid}/save-as-ai-example`
2. **Endpoint** (`main.py:save_sheet_as_ai_example`):
   - Берёт все estimate_takeoffs sheet'a
   - Деактивирует предыдущие examples на этом sheet (active=0)
   - INSERT в `ai_trace_examples` (active=1)
3. **Few-shot в AI Trace** (`cv_trace.py:label_contours_with_ai`):
   - `_load_gold_example()` — берёт самый свежий active example
   - Рендерит его image + numbered overlay + Артёмовы labels как **reference block** перед основной задачей в Sonnet content
   - Sonnet видит «вот так expert сделал» → подражает granularity и ignore-rules
4. **Sonnet fallback на Haiku** при 429 — few-shot reference остаётся в prompt (Haiku тоже умеет, чуть хуже)

## Таблица `ai_trace_examples`

```
id PK
sheet_id FK estimate_sheets, estimate_id FK estimate_projects
image_path (snapshot, чтобы пример не сломался при удалении sheet)
polygons_json: [{kind, label, polygon, closed}]   ← snapshot Артёмовых takeoffs
n_takeoffs, project_type, sqft, notes
accepted_at, accepted_by (user id)
active (0/1) — при повторном save_as_example на том же sheet старая запись 0
```

Index `ix_ai_trace_examples_active_recent (active, accepted_at DESC)` — селект «свежайший accepted» O(1).

## Что не реализовано (Phase 2+)

- **Similarity matching** — сейчас берётся **один свежайший** example. Лучше: при AI Trace найти 1-2 examples с похожим `project_type`/`sqft` ±25% и положить как 2 references (multi-shot).
- **Rules extraction** — Артём может явно сохранить «правило» через UI («never split ribbed cladding», «top 15% = sky»). Идут в `learned_rules` уже существующей таблицы (см. `siding-estimator-bot/save_learned_rule`).
- **Per-page-type templates** — separate examples for «commercial multi-elevation» vs «residential single elevation» — нужны теги project_type точнее.

## Файлы

- `backend/main.py:save_sheet_as_ai_example`, `list_ai_trace_examples`
- `backend/cv_trace.py:_load_gold_example`, `label_contours_with_ai` (few-shot block)
- `src/api/client.js:saveSheetAsAiExample`
- `src/pages/SheetEditorPage.jsx` — кнопка «Teach AI» 🤖 (emerald)
- `backend/tsa.db` — таблица `ai_trace_examples`

Связано: [[project-estimator-ai-memory]] (.md файлы в estimator_memory/), [[project-estimator-assemblies]], [[feedback-cv-trace-over-ai]], [[feedback-ai-trace-enabled]], [[feedback-estimating-metric]].
