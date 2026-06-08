---
name: feedback_estimator_name_lookup
description: Estimator bot+AI must resolve project NAME→estimate_id (find_estimate_by_name / GET /api/estimates/search); never ask human for numeric id
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e7f5a3a4-b20d-49e3-b55b-d7c47ac998fc
---

Артём (2026-06-04): главная боль — haiku-бот «не находил загруженные файлы» и
дёргал человека, когда ему давали проект СЛОВАМИ («Sage Hill Bldg 600»).
Причина: не было name→estimate_id lookup. Бот открывал проект только по
deep-link `/start estimate_<id>`.

**Фикс (deployed 2026-06-04):**
- Bot tool `find_estimate_by_name(query, limit)` в `siding_tools.py` —
  token-LIKE по name И address (каждое слово отдельно), вызывать ПЕРВЫМ когда
  проект назван словами. Зарегистрирован в TOOL_DISPATCH + schema.
- Backend `GET /api/estimates/search?q=&limit=` в `backend/main.py` (до
  параметрического `/api/estimates/{eid}` — route-order, см [[feedback_fastapi_route_order]]).

**Why:** «Sage Hill 600»/«Kensington»/«B600» теперь все резолвятся в estimate #3.
**How to apply:** бот НИКОГДА не должен говорить «не вижу файлов» / просить id —
сначала find_estimate_by_name → get_ontime_estimate(id) → auto_trace_estimate(id).

⚠ Drift в `/root/ontime/CLAUDE.md`: реальный backend = `/root/ontime/backend/main.py`
(не `/root/ontime/main.py`), prod DB = `backend/tsa.db`, сервисы =
`ontime-api.service` + `ontime-bot.service` + `siding-estimator-bot.service`
(не `ontime`). Estimator-бот ЖИВОЙ (active), репо `/root/siding-estimator-bot`.

**Доп. фиксы 2026-06-04 (deployed):**
- **Бот язык:** SYSTEM_PROMPT был почти весь на русском → бот отвечал по-русски
  несмотря на «reply in English». Добавлен HARD-RULE блок про English вверху +
  FINAL REMINDER внизу + greeting/`_load_estimate_summary` переведены на EN.
  Дефолт — English (TSA team / Ihor M); RU только по явной просьбе.
- **Arch#1:** `live_knowledge_block()` (siding_tools.py) теперь инжектит не только
  learned_rules + rules/*.md, но и standing-instructions lessons (по ключам
  instruction/scope/calibrate/standard-working-procedure/assemblies-reference/
  trim-terminology) + каталог всех lessons/ (cap 14000). Бот всегда знает всю
  библиотеку Ihor, материал-гайды тянет по требованию memory_read.
- **Arch#2:** `cv_trace.py::_estimator_guidance_block()` инжектит конвенции Ihor
  (legend/assemblies/scope/trim) в CLASSIFY-промпт — AI Trace учится не только на
  ai_trace_examples-картинках, но и на тексте.
- **Arch#3 (единый источник правил):** `save_learned_rule` зеркалит активные
  learned_rules в `rules/learned-rules-from-corrections.md` (виден в Memory UI);
  BOM `_lookup_learned_waste` имеет fallback `_md_waste_override()` — читает
  hand-written rules/*.md (есть waste-james-hardie.md 10%). Итог: и бот, и BOM,
  и UI видят ОДИН набор правил (DB ⇄ .md), без дрейфа.
- **UI:** кнопка «🤖 AI / Спросить AI» добавлена на EstimatingPage (список) и
  SheetEditorPage (тулбар); HelpButton переделан в центр-модалку (раньше absolute
  popover обрезался на мобиле).

Takeoff-реальность: AI auto-trace (cv_trace.py, CV+Claude Vision) пока даёт
ЧЕРНОВИК — на B600 выдал 4 частичных полигона на 1 элевации, калибровка рваная
(px_per_ft 19 vs 42 на соседних листах). Корректный takeoff по материалам
(Lux/Metal) сам не сделает. Путь — teaching loop: Ihor M (estimator director)
обводит/правит в OnTime UI → `ai_trace_examples` → cv_trace берёт как few-shot
(main.py ~20711, cv_trace.py ~574). Оба surface (бот+UI-AI) учатся из одной
общей БД + estimator_memory + learned_rules. См [[project_estimator_ai_memory]],
[[project_ai_trace_teach]], [[feedback_cv_trace_over_ai]].
