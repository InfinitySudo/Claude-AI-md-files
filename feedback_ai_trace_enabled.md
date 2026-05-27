---
name: feedback-ai-trace-enabled
description: Vision-tracing для OnTime estimating РАЗРЕШЕНО Артёмом 2026-05-25 (Уровень 2 — AI draft + ручная проверка)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3f969d3c-e080-450e-8ce9-fb152339bbc0
---

# Vision Auto-Trace разрешено (2026-05-25)

Артём явно попросил: "ua hochu chtobi ai agent obvel vse, a ya proveru" — то есть
Уровень 2 из договорённости 2026-05-25 (AI делает draft polygon-обводки,
человек правит/принимает).

**Why:** ручная обводка 28+ страниц blueprint'a (Sage Hill Bldg 600) занимает
несколько часов; AI делает это за минуты, человек только корректирует. ROI
очевиден если accuracy AI хотя бы 60-70%.

**How to apply:** реализовано как:
  • `POST /api/estimates/{eid}/sheets/{sid}/ai-trace` — обводка walls/openings/soffit/fascia/gable
  • `POST /api/estimates/{eid}/sheets/{sid}/ai-calibrate` — auto-detect dimension line + px_per_ft
В UI SheetEditorPage 2 кнопки: 📐 AI (calibrate) и 🤖 AI Trace.
Backend client: `/root/ontime/backend/ai_trace.py`.
Использует Claude Sonnet 4.6 Vision через OAuth (как siding-estimator-bot).
Takeoffs получают label с префиксом '🤖 ...' чтобы отличать AI от ручных.
При auto-calibrate area/perim существующих takeoffs пересчитываются.

**Отношение к [[feedback-estimating-no-api]]:**
Старый запрет (2026-05-04) касался ДРУГОГО кейса — авто-extraction project
metadata из uploaded PDF при загрузке (там нужно было читать названия,
адреса, типы из текста). Тот запрет остаётся в силе для extraction.

Vision-tracing — новый workflow. Не противоречит старому запрету:
  • Не делает silent decisions — каждый polygon видим, можно удалить
  • Не блокирующий — без него обводка работает как раньше
  • Под управлением пользователя — нужно явно нажать кнопку
  • Помечается префиксом 🤖 — никогда не путается с ручной работой
