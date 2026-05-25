---
name: cv-trace-over-ai
description: "На blueprints OpenCV findContours > AI Vision для polygon-trace; Sonnet рисует bbox'ы вместо контуров"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a7860ae7-e5ec-4b08-a0dc-c01b073078ff
---

В OnTime Estimator (`backend/ai_trace.py` + `backend/cv_trace.py`) endpoint `/api/estimates/{eid}/sheets/{sid}/ai-trace` работает по гибриду:
1. **OpenCV** (Canny→Otsu→morphology close→findContours EXTERNAL→approxPolyDP) находит pixel-precise контуры зданий
2. **Claude Haiku Vision** опционально классифицирует kind/label по пронумерованному overlay
3. Дефолт kind=wall, label="contour N" если AI label не доехал

**Why:** Sonnet 4.6 и Haiku на architectural blueprints упорно возвращают **прямоугольные bbox'ы** даже с супер-строгим prompt'ом ("trace actual visible lines", "do not bbox", etc.). Это fundamental limitation VLM — pixel-grounding в нормализованных координатах слабый, особенно на чертежах с несколькими elevations на одной странице. На sheet 19 estimate 3 проверено визуально 2026-05-25: Sonnet выдал 13 bbox'ов, многие смещены и попадали в чужой elevation; CV findContours дал 2 идеальных полигона по контуру зданий.

**How to apply:**
- Не возвращайся к чистому AI-trace pipeline в OnTime — это известно сломанный путь.
- Если нужно AI auto-trace в другом проекте на blueprints (Wrestling/Trading/Tutor) — используй ту же связку: CV-contours + AI-labels поверх.
- Если CV ничего не находит — у sheet'а нет solid color fills (только linework). Артёма уведомить, fallback на ручную обводку.
- Параметры в `cv_trace.py`: MIN_AREA_FRAC=0.005, MAX_AREA_FRAC=0.4, MAX_VERTICES=30, MAX_CONTOURS=40. Тюнить если sheet'ы радикально другие.
- Связано: [[feedback_ai_trace_enabled]], [[feedback_anthropic_key_scoped_estimator]], [[project_tsa_estimating]].
