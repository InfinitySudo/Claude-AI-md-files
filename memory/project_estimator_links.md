---
name: estimator-links
description: estimate_projects (OnTime PDF) ↔ stack_projects (TG bot Excel BOM) связаны через project_links
metadata: 
  node_type: memory
  type: project
  originSessionId: a7860ae7-e5ec-4b08-a0dc-c01b073078ff
---

В `tsa.db` две таблицы для разных представлений проекта:
- **`estimate_projects`** — OnTime PDF blueprints + takeoffs. Создаётся через UI Upload PDF.
- **`stack_projects`** — Stack CT mirror, наполняется через `siding-estimator-bot` (Excel imports + Stack API). Нумерация ОТДЕЛЬНАЯ — естественно не совпадает с estimate_projects.

С 2026-05-25 связаны через **`project_links`**:
```sql
CREATE TABLE project_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  estimate_project_id INTEGER NOT NULL,
  stack_project_id INTEGER NOT NULL,
  linked_by INTEGER,
  linked_at TEXT,
  auto_matched INTEGER DEFAULT 0,
  match_score REAL,
  UNIQUE(estimate_project_id, stack_project_id)
);
```

**Backend endpoints** (`main.py`):
- `GET /api/estimates/{eid}/stack-links` — список linked
- `POST /api/estimates/{eid}/stack-links` body `{stack_project_id}` — link
- `DELETE /api/estimates/{eid}/stack-links/{sid}` — unlink
- `GET /api/stack-projects` — список всех для picker

**UI:** `StackLinksPanel` в `EstimateDetailPage.jsx` — «🔗 Linked Excel BOM imports».

**Bot:** `get_ontime_estimate` теперь возвращает `linked_stack_projects` массив — бот может сразу `get_project_bom(stack_id)` для baseline.

**Why:** одна и та же стройка имеет несколько data sources (PDF blueprint + Excel BOM revisions); merge в одну таблицу сломал бы schema (разные поля). Linking даёт flexible relationship без destructive миграции.

**How to apply:**
- Новый Excel BOM в TG бота → создаёт stack_project с новым id; Артём вручную линкует через UI (auto-link можно добавить позже — fuzzy match по name работает 75% на текущей выборке, порог 0.55).
- Один estimate может иметь несколько linked stack_projects (draft + final + change-orders).
- Связано: [[project_tsa_estimating]], [[project_estimator_ai_memory]].
