---
name: project_gerchik_proboi_subtypes
description: Gerchik-агент — подвиды пробоя (с базой/с лету/с закреплением) + разрез аналитики by_setup_type
metadata: 
  node_type: memory
  type: project
  originSessionId: 9267277e-3df1-4ed4-9b88-ec9b23834f86
---

Подвиды стратегии ПРОБОЙ в Gerchik-агенте (PumpDumpAI_Agent), ветка `feature/proboi-subtypes`, commit 4855792 (PR-1 уже в main отдельно).

`proboi_subtype(close, level_price, atr, squeeze, tight_zone)` в `src/gerchik/pipeline.py` классифицирует пробой по курсу:
- **с базой** — поджатие/узкая проторговка перед уровнем (squeeze или tight_zone) → приоритет над импульсом
- **с лету** — импульсный пробой ≥1×ATR за уровень, базы нет
- **с закреплением** — чистое закрытие за уровень без импульса/базы (atr=0 → тоже сюда)

`PreThesis.setup_type` теперь несёт подвид (`пробой·<sub>`); для отбоя/ЛП = имя стратегии. Аналитика: `analytics.by_setup_type` (разрез `period_report`) + панель «по подвиду» в `web.py`. Тесты: классификация + агрегация. Связано с [[project_gerchik_strategy_extraction]], [[feedback_gerchik_example_numbers]].

⚠ Рефлектор (недельный) отложен — у Gerchik-агента ещё нет закрытых сделок (только 2 живые ЛП: BTCUSDT/XRPUSDT).
