---
name: project_gerchik_checklist_expanded
description: "Чек-лист предпосылок дозакрыт под списки Артёма — +9 детекторов (close-под-экстремум, откат, консолидация, дистрибуция, задёрг…); checklist_min 0.5→0.45"
metadata: 
  node_type: memory
  type: project
  originSessionId: 3814021d-32b9-44d3-87ae-8a21ce804338
---

2026-06-13: аудит «реализованы ли все предпосылки Артёма» → ~13 ✅ / ~5 🟡 / ~4 ❌. Дореализовал
недостающие как НОВЫЕ пункты чек-листа (checklist.py, считаются в гейте ≥checklist_min + edge):
ПРОБОЙ +5: `close_at_bar_extreme` (закрытие под High/Low бара #10), `shallow_pullback` (<30% ATR
откат/нет продавца #6,#12), `long_consolidation` (длинная база #4), `no_lp_reaction` (#8),
`impulse_absent` (нет импульса где ждали #9).
ОТБОЙ/ЛП +4: `long_runup_no_pullback` (длинное безоткатное #1), `htf_distribution` (раздача на ТФ #3),
`impulse_absent` (#7), `counter_trend_spike` (задёрг против тренда #10).
+ проброшен `side` в ctx (pipeline build_setup).

⚠ Калибровка (замер на истории, 10248 near-моментов): частоты True — close_extreme 19%, shallow_pb 26%,
long_consol 30% (после фикса; было 0% — слишком строгий), no_lp_react 2%, no_impulse 5%, long_runup 10%,
distribution 51%, ct_spike 49%. Редкие (no_lp/no_impulse) — это РЕАЛЬНО редкие признаки (награда за
чистый сетап), но удлинение списка топило ПРОБОЙ (тип. 0.60→0.45). Поэтому `checklist_min` 0.5→0.45
(config) — пробой не задыхается, ЛП/отбой (0.63) не задеты. Живьём ≥45%.

Остаётся качественным (правилами плохо, ждёт Vision-судью §10.1): «отсутствие импульса там где должен» —
сейчас прокси по малым телам баров. Дистрибуция HTF — прокси по D (не по недельному объёму).
Дополняет [[project_gerchik_style_selection_gates]] [[project_gerchik_checklist_gate]]. Не закоммичено.
