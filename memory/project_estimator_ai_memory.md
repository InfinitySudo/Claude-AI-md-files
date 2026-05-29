---
name: estimator-ai-memory
description: .md memory shared между OnTime backend и TG ботом @TSA_EstimatorBot
metadata: 
  node_type: memory
  type: project
  originSessionId: a7860ae7-e5ec-4b08-a0dc-c01b073078ff
---

В `/root/ontime/backend/estimator_memory/` живёт постоянная файловая память AI Estimator'а — `.md` файлы по 5 категориям (`lessons/`, `rules/`, `vendors/`, `materials/`, `projects/`) + auto-generated `INDEX.md`. Общая для:
- TG бот `@TSA_EstimatorBot` (`/root/siding-estimator-bot/`) — 4 tools: `memory_index`, `memory_read`, `memory_search`, `memory_save`. System prompt требует вызвать `memory_index()` **ПЕРВЫМ** перед любым новым эстиматом и подгрузить все `rules/*` + релевантные `vendors`/`materials`/`lessons`.
- OnTime backend — endpoints `/api/estimator/memory[/file/{path}|/search]` GET/POST/DELETE.
- OnTime UI — `EstimatorMemoryPage.jsx` на `/estimating/memory`, кнопка **🧠 Memory** в toolbar `EstimatingPage`. CRUD entries вручную.

**Why:** Артём 2026-05-25 явно попросил «чтобы AI агент помнил всё чему его учат и перед новым проектом просматривал необходимые данные». До этого `learned_rules` table в `tsa.db` была единственным каналом learn'инга, но плохо browse'ил'ась + не shared с TG бот workflow.

**How to apply:**
- Когда Артём учит durable правилу (waste factor, vendor lead time, material quirk) — бот должен сам `memory_save(category, title, body)` без напоминания.
- Артём может править/добавлять entries прямо в OnTime UI на `/estimating/memory`.
- Связано: [[project_tsa_estimating]], [[project_estimating_industry_rules]], [[project_estimating_phase_a]].
