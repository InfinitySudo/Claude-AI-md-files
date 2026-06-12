---
name: feedback_gerchik_proboi_side_inversion
description: "Баг side-инверсии пробоя в Gerchik paper-агенте — сторону решает стратегия, не level.kind"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5953d251-e235-4db9-839e-85e0af7d45ee
---

В Gerchik-агенте (`/root/PumpDumpAI_Agent`, branch main, `src/gerchik/`) сторона сделки ДОЛЖНА браться из стратегии (`trig["side"]`, теперь `PreThesis.side`), а НЕ выводиться из `level.kind`.

**Why:** `_side_from_level_kind` (resistance→SHORT, support→LONG) верен ТОЛЬКО для фейд-стратегий (отбой/ЛП). Для **пробоя** сторона обратная (resistance пробит вверх→LONG, support вниз→SHORT — это продолжение, не фейд). `paper_engine.on_signal` и `runner.py` переопределяли сторону через level.kind → пробой открывался с инвертированной стороной: геометрия SHORT (стоп ВЫШЕ входа, цель ниже), но позиция LONG → «стоп» срабатывал в прибыль на том же тике → фейковые +1R, рунэвей-реентри каждые ~45с (116 сделок DOGEUSDT, фейк 100% WR / +98.52$) + 429-шторм Claude от переоценки.

**How to apply:** 2026-06-12 фикс — `PreThesis.side` (из пайплайна) + `_side_of(thesis)` в runner + `t.side` в paper_engine + защитный гейт `inverted_geometry` (REJECT если для LONG stop≥entry или tp≤entry). Стата пробоя до фикса — мусор. См. [[project_gerchik_proboi_subtypes]], [[project_gerchik_strategy_extraction]], [[feedback_one_tweak_at_a_time]].
