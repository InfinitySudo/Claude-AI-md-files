---
name: project_estimating_ai_trace
description: "OnTime AI Trace overhaul — classify coloured/linework gate, region-scoped trace per elevation, material-labelled; works only on colour-filled sheets"
metadata: 
  node_type: memory
  type: project
  originSessionId: e7f5a3a4-b20d-49e3-b55b-d7c47ac998fc
---

2026-06-04: AI Trace выдавал мусор (рандомные прямоугольники по РАЗНЫМ элевациям,
все подписаны «Northwest», бо́льшая часть стен не обведена). Корень: `cv_trace.py` =
color-сегментация по ВСЕМУ листу (k-means по квадрантам, топ-30 пятен) — нет понятия
элевации/материала, и не работает на linework.

Изучены все 5 проектов — они РАЗНЫЕ (см lesson `project-blueprint-profiles.md`):
#3 Sage Hill metric/coloured, #4 Sage Walk imperial/coloured, #5 Pinegate imperial/
linework, #6 Truman imperial/91pp/portrait, #7 Livingston metric/linework+signage.

**Фиксы (план crystalline-sniffing-tower, A+B; C — позже эксперимент):**
- **W1 gate** `cv_trace.classify_sheet()` — COLOURED только если colour-fill ≥3% И
  крупнейшая связная цветная область ≥2.5% (отсекает зелёные signage-боксы #7).
  Endpoint `ai_trace_sheet` на linework возвращает `advise:'manual'` (не сегментит);
  фронт спрашивает «trace anyway» (force). 3 из 5 проектов — linework.
- **W2 калибровка**: `detect_scale` scale_ratio понимает imperial нотацию
  (1/4"=1'→48, 1/8"→96, 3/16"→64, 1/2"→24, 1"=20'→240); `_pdf_page_width_mm`
  rotation-safe (Truman рендерится landscape из portrait box).
- **W3 region-scoped (A)**: `detect_contours(region)`/`trace_sheet(region,materials)`/
  `render_numbered_overlay(region)` — обводка внутри одной элевации, AI видит только
  её, метит по `estimate_projects.siding_type`. Endpoint принимает `region`/`force`.
  Фронт: tool «Elev» (рамка 2 клика) → AI Trace скоупится. SheetEditorPage.jsx.
- **B**: ручной полигон + верные площади (калибровка) + Teach AI — основной путь,
  особенно для linework.

**C ИНТЕГРИРОВАН (commit 180eb7e):** `cv_trace.detect_by_material(image_path, region)`
— локальный LAB k-means внутри элевации, маска на каждый цвет облицовки → контуры
по МАТЕРИАЛАМ, с чисткой (near-white bg, region area-frac, sliver + thin-slash extent,
snap rectilinear, IoU dedupe). `trace_sheet`: при region (цветная элевация) → C
(engine 'cv-material'), fallback на A если C пусто. На #3 C дал 4 чистые материал-зоны
(tan/dark-metal/masonry) против 3 перекрывающих блобов A; покрытие 100% vs 94%,
точность 36% vs 20%. C = лучший ЧЕРНОВИК по материалам, дочистка человеком (B).

⚠ Истина: color-CV не обводит элевации идеально (C точность ~36%, перекрывает фон) —
это черновик под gate; на linework — только ручками (C/A не запускаются).
См [[project_estimating_calibration_explainability]], [[feedback_cv_trace_over_ai]],
[[feedback_ai_trace_enabled]], [[project_ai_trace_teach]].
