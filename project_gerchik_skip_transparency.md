---
name: project_gerchik_skip_transparency
description: "Gerchik paper-агент — панель «Почему пропущено»: per-symbol×strategy причины скипа за цикл сканера"
metadata: 
  node_type: memory
  type: project
  originSessionId: 633d8a35-ad14-424a-8058-acee61df1e01
---

Прозрачность «Почему пропущено» в Gerchik paper-агенте (PumpDumpAI_Agent, PR #4, main 8408bfa,
ветка feature/skip-transparency, 279 тестов).

**Зачем:** «нет сделки» было неотличимо от «нет работы» — Артём не видел, почему ~25 ликвидных
монет молчат. Причины терялись: `build_setup` схлопывал всё в `no_setup`, гейт сканера (is_tradeable)
отсекал до `on_signal`.

**Как:**
- `src/gerchik/skips.py` — процессный синглтон `SkipLedger` (демон = ОДИН процесс: сканер ПИШЕТ
  begin/record/end_cycle, панель ЧИТАЕТ snapshot; двойная буферизация — пустой цикл не затирает снимок).
- `pipeline.Decision.code` (машинный код) + опц. `trace` в `build_setup` → гранулярные коды вместо
  `no_setup`: no_levels / no_level_near / no_trigger / chasing_exhausted / bad_geometry / take / judge_reject.
- `scanner._step_symbol`: пишет код по каждому (символ×стратегия), включая гейты `not_enough_klines` /
  `not_tradeable` и `in_position`.
- `web.py`: `/api/skips` + карточка «Почему пропущено» (агрегат по причинам + список символов).

**Живой срез (33 символа × 3 стратегии = 99/цикл):** 53 no_level_near, 24 not_tradeable, 12 no_trigger,
10 in_position. Подтверждает: throughput упирается в «цена далеко от уровня» (режим рынка), а не в гейты.

Панель :8095 (ui_host 127.0.0.1, ui_port из config). Связано: [[project_gerchik_strategy_extraction]],
[[project_gerchik_proboi_subtypes]], [[feedback_gerchik_turnover_partial_day]].
