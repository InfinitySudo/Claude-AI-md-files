---
name: TSA company role overlaps
description: В TSA (company_id=1) Director совмещает функцию Purchasing Manager; Artem Borysiuk одновременно admin+author
type: project
originSessionId: f1c65322-19fe-4461-86eb-62acb1eaf226
---
**Текущая расстановка ролей в TSA** (на 2026-04-21):

| User id | ФИО | `users.role` | Совмещения |
|---|---|---|---|
| 4 | Artem Borysiuk | admin | владелец; часто выступает автором Extra Work |
| 77 | Mike Kripak | pm | |
| 85 | Ola | vp_construction | |
| 86 | ARTEM TKACHENKO | director | **+ Purchasing Manager** (в штате отдельного purchasing нет) |
| 81 | Yuliia Kapshiienko | accountant | |

**Как это учитывать в коде:**
- В `pm_approve_extra_work` (`main.py`): если `notify_role_with_store(purchasing_manager)` вернул 0 получателей, fallback — оповестить director с таким же action_required. Реализовано 2026-04-21.
- `/api/extra-work/{eid}/order-materials` allowed_roles = `('purchasing_manager', 'admin', 'director')` — чтобы director мог выполнить действие.
- Если добавится новая роль, которую кто-то должен покрывать — использовать тот же fallback-паттерн, либо добавить helper `notify_role_or_fallback(role, fallback_role)`.

**Why:** Purchasing как штатная единица отсутствует, но процесс заказа материалов всё равно должен кем-то двигаться. Director взял на себя эту функцию.
