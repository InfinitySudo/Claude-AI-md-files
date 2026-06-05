---
name: project_estimating_calibration_explainability
description: OnTime estimating calibration is now verifiable — calib_json stores how px_per_ft was derived; UI shows metric+imperial breakdown + reference line
metadata: 
  node_type: memory
  type: project
  originSessionId: e7f5a3a4-b20d-49e3-b55b-d7c47ac998fc
---

2026-06-04: Artem/Ihor M не понимали «Scale: 42.1 px/ft (23200 (mm·AI))».

**Как AI считает калибровку** (ai_trace.py): Claude Vision (`detect_scale`,
MODEL_CALIBRATE=Haiku) находит ОДНУ размерную линию (приоритет — overall building
width), возвращает p1/p2 (normalized), `feet` (длина в футах из любых единиц),
label_raw, unit_detected, system_evidence. `scale_to_px_per_ft` → px_distance между
точками, `px_per_ft = px_distance / feet`. Пример: «23200» mm = 23200/304.8 = 76.115 ft;
линия 3204 px → 42.095 px/ft. Санити-гард PPF 3..500 + cohort-confidence
(`_calibration_confidence`).

**Что было не так:** считались p1/p2, px_distance, feet — но НЕ сохранялись;
в БД только px_per_ft + 40-симв. scale_label. Проверить было нечем.

**Фикс (deployed):**
- `estimate_sheets.calib_json` (новая колонка, миграция в main.py ALTER-списке).
  AI-калибровка (`ai_calibrate_sheet`) и ручная (PATCH `SheetPatch.calib`, ruler)
  сохраняют {source, p1_px, p2_px, px_distance, feet, px_per_ft, label_raw,
  unit_detected, system_evidence, notes, calibrated_at}. Ручная без calib чистит
  stale-ref.
- SheetEditorPage: «Scale …» теперь кнопка → `CalibrationInfoModal`. Показывает
  МЕТРИКУ И ИМПЕРИЮ: реальная длина 23 200 mm (23.20 m / 76′ 1″), measured px,
  «3204 px ÷ 76.12 ft = 42.1 px/ft», источник (AI/manual), how-to-verify, и
  чекбокс «show reference line» рисует p1→p2 фиолетовым на canvas.
  Хелперы `explainCalibration()` + `ftToFtIn()`.
- Старые калибровки (без points) → fallback-текст «re-calibrate to pin line».
  Sheet #19 (Sage Hill p.16) бэкфилл math (px_per_ft неизменён).

**2026-06-04 — AI калибровка ловилась на вранье, добавлены гарды:**
На Sage Hill p.16 AI выдумал размер «23200 mm» (его НЕТ в тексте листа) и провёл
линию по пустому полю + блоку keynotes. Проверено: pdftotext show «23200»
отсутствует. → Это доказывает: AI auto-calibrate НЕЛЬЗЯ доверять без гардов.

Фикс (main.py ai_calibrate_sheet, deployed commit 1e595e1):
- `_vector_printed_numbers()` — тащит реально напечатанные числа с координатами
  (pdftotext -bbox → px), передаёт в `detect_scale(printed_numbers=...)`; AI обязан
  выбрать label_raw ИЗ них (не выдумывать). Headless auto-trace тоже покрыт (зовёт
  ту же функцию).
- 3 гарда отклоняют калибровку (px_per_ft НЕ применяется, просят manual):
  (a) числа нет среди напечатанных; (b) `_label_to_feet()` value-в-юните ≠ feet >5%
  (поймал кейс 97030mm vs 76ft); (c) число дальше 10% диагонали от линии.
- calib_json хранит grounded/anchor для прозрачности.
- UI стал px-free: headline = реальный размер (mm/m + ft-in), плюс прозрачная
  формула «how the scale is calculated» в обеих системах через "image dots"
  (Ihor видит расчёт). Линия-эталон без px в подписи.
- Урок `lessons/how-to-calibrate-scale-correctly.md` (общий бот+UI).

⚠ Вывод: Vision не умеет надёжно мерить scale даже с grounding (выбирает число,
но геометрия не сходится). Источник правды = ручная калибровка 📏; AI = черновик
под гардами + человеческая проверка.

**2026-06-04 — правильная калибровка p.16 через PLOT-SCALE:**
Лист p.16 целиком **1:100** (подтвердил Артём — мой ранний вывод про dual-scale
1:100/1:150 был ОШИБОЧНЫМ, снят). Размеры/подписи на элевациях — векторные
пути, не текст → pdftotext их не видит (только таблицы/keynotes). Поэтому самый
надёжный способ = plot-scale: paper ровно 1000.0 мм (PDF 2834.64pt) ÷ render 5394px
= 5.394 px/мм бумаги; при 1:100 → **16.44 px/ft** (1 м = 53.9 px). Это ТОЧНО и не
зависит от пиксельного промера. Sheet 19 откалиброван на 16.441, проверочная линия
по габариту здания = ~25.5 м (sane). Формула: px_per_ft = (render_px/paper_mm)/scale_ratio×304.8.
TODO (предложено Артёму): показывать ожидаемый px/ft из печатного масштаба прямо
в окне калибровки.

См [[feedback_estimator_name_lookup]], [[feedback_cv_trace_over_ai]],
[[feedback_estimating_metric]].
