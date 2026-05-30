---
name: project-tsa-orders-queue-visibility
description: "OnTime Procurement «Orders queue» = GET /purchase-orders?mine=true; менеджмент/закупки видят все PO компании, foreman — только свои; ловушка 5 учёток Артёма"
metadata: 
  node_type: memory
  type: project
  originSessionId: 520ebb72-e212-4d77-8428-d58bac900b5b
---

OnTime ProcurementPage вкладка **Queue** («Orders queue») грузится через `api.purchaseOrders.listMine()` → `GET /api/purchase-orders?mine=true` (`backend/main.py:list_pos`). Группировка на фронте по статусу: drafts / pending_* / approved+sent+partially_received / terminal.

**Логика видимости (после fix 2026-05-29, commit 1a49448):**
- `MANAGEMENT_ROLES` (`admin,pm,vp_construction,director,director_estimator`) + `purchasing_manager` → видят **ВСЕ PO компании**.
- Остальные (foreman) → только `created_by_user_id = me` ИЛИ ожидающие их апрува (`pending_purchasing/pm/director` по их роли).
- До фикса `mine` отдавал только own+awaiting для всех → `sent`-PO, созданный под другой учёткой, не показывался нигде в очереди. Плюс был AND/OR precedence-баг: ветки `pending_*` уходили из-под `company_id` (cross-company leak) — обёрнуто в скобки.

**Ловушка — у Артёма 5 учёток в TSA (company_id=1), легко спутать кто created_by:**
| id | full_name | role |
|--|--|--|
| 4 | Artem Borysiuk | admin |
| 8 | Artem Borysiuk | pm |
| 14 | Artem Huridov | foreman |
| 17 | Aleksandr Taranenko | installer |
| 86 | ARTEM TKACHENKO | director |

PO-2026-0001 был создан под id=86 (director), а смотрел очередь под другой → отсюда «почему нет моего PO». При дебаге видимости PO/задач — сверять `created_by_user_id` с конкретной учёткой, а не «Артём вообще».

Связано: [[project-tsa-procurement]], [[project-tsa-roles-access]], [[feedback-fastapi-route-order]]. БД prod: `/root/ontime/backend/tsa.db` (env `TSA_DB_PATH`, дефолт backend/tsa.db — НЕ data/ontime.db из CLAUDE.md). Сервис: `ontime-api.service` (CLAUDE.md говорит `ontime` — drift).
