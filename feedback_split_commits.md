---
name: Split Commits Over Speed
description: Артём предпочитает чистую историю с отдельными коммитами на каждую фичу, даже когда я могу bundle для скорости
type: feedback
originSessionId: 76d69d60-e032-4a5a-9b40-2a8d16aee677
---
Когда в working tree висит несколько связных, но логически разных фич — делать отдельный коммит на каждую, а не bundle под предлогом «быстрее».

**Why:** 2026-05-03 я запушил «WIP catchup» одним коммитом (timesheet + service kanban + BOM picker + delivery role + scoring backfill = 10 файлов, 2455 строк), оправдав это «Artem prefers speed». Артём поправил: «mozhesh sdelat krasivo ne nujno speshit». Чистая история ценнее скорости коммита, особенно когда фичи реально независимые.

**How to apply:**
- Если в working tree пересекаются 2+ независимых feature streams — коммитить отдельно (использовать `git apply --cached` с patch-файлами для изоляции hunks внутри одного файла, как делал с ProjectDetailPage в этой же сессии)
- Bundling OK только когда фичи реально цепляются (общий рефактор, или одна фича через несколько файлов)
- `feedback_no_routine_confirms.md` (делать без подтверждений) применимо к **выполнению** работы, не к **структуре коммитов** — для коммитов чистота приоритетнее
- Если bundling уже произошёл и запушен — не пытаться force-push (запрещено `feedback_auto_push_default.md`); revert+redo или принять как есть, спросив пользователя
