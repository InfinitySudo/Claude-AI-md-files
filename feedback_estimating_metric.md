---
name: feedback-estimating-metric
description: "OnTime Estimating поддерживает и imperial и metric чертежи. Внутренняя единица — всегда px_per_ft (футы), но UI и AI prompt принимают оба типа input/output."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a7c17f24-1434-4a2c-b45d-6a43248a8f2f
---

Артём 2026-05-27: чертежи компании бывают в imperial (US) и metric (Canada/EU). Раньше калибровка была только imperial.

**Где живёт правка:**

1. **Manual calibrate** — `/root/ontime/src/pages/SheetEditorPage.jsx` `CalibrationModal`:
   - Toggle Imperial/Metric (запомнено в `localStorage.calibrate_unit`)
   - `parseFeetInches` остался; добавлен `parseMeters` («3.5», «3.5 m», «350 cm», «3m 50cm»)
   - При metric: метры → ft через `× 3.2808398950131235` → существующий `px_per_ft` поток
   - `scale_label` сохраняет ввод + единицу: `"3.5 m (m)"` / `"10'-6\""`

2. **AI auto-calibrate** — `/root/ontime/backend/ai_trace.py` `CALIBRATE_PROMPT`:
   - Step 0 «DETECT DIMENSION SYSTEM» — модель сначала ищет title block notes («ALL DIMENSIONS IN MILLIMETERS», «1:50», «1/4\" = 1'-0\""»), потом анализирует ticks/suffixes, потом гео-эвристика
   - Все примеры конверсий перечислены в response schema (mm/304.8, m×3.2808, cm/30.48)
   - Возвращает `unit_detected` ∈ {`imperial_ft_in`, `imperial_decimal_ft`, `metric_mm`, `metric_m`, `metric_cm`} + `system_evidence` (брив. why)

3. **Display** — `main.py:ai_calibrate_sheet` тег в label:
   - metric → `"23200 (mm·AI)"`
   - imperial → `"76'-4\" (ft·AI)"`

**Why px_per_ft а не px_per_meter в БД**: BOM формулы, vendor catalogue, `SIDING_SYSTEMS`, takeoff area_sqft / perimeter_lf — всё в imperial. Менять везде = месяц работы. Конверсия на boundary (UI input + AI extraction) даёт ту же точность за минимум кода.

**How to apply**:
- Если AI выдаст `px_per_ft` вне реалистичного диапазона на metric-чертеже → отвергнется sanity-check'ом (`PPF_MIN=3, PPF_MAX=500`) и Артём калибрует вручную — теперь с metric toggle
- Если Артём видит «foot-tick» в label на metric-чертеже → AI не задетектил metric, нужно расширить prompt examples
- Все 3 файла бэкаплены `.bak_20260527_*` рядом

Связано: [[project-tsa-estimating]], [[project-estimating-phase-a]], [[feedback-ai-trace-enabled]], [[feedback-cv-trace-over-ai]].
