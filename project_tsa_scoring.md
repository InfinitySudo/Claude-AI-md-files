---
name: OnTime Scoring (points)
description: Тиры и формула points за completion в OnTime — пересмотрены 2026-04-27 чтобы устранить дисбаланс с punctuality
type: project
originSessionId: 2698e6df-f89c-4d5c-ae55-ba7c1be6f1d9
---
**TIER_BASE** в `main.py:2694` (после ребаланса 2026-04-27):
- S (≤$25k): **250**
- M ($25–50k): **500**
- L ($50–100k): **1000**
- XL (>$100k): **2000**

Старые базы (50/150/350/700) проигрывали punctuality: Igor с 16 рабочими = 352 punctuality/мес против 65 за S-проект — 1 проект ≈ 4 дня дисциплины.

**Формула** (`compute_points`, `main.py:2710`):
- `points = max(0, base + deadline_adj + hours_adj)`
- deadline: ≥10 дней раньше → +30% базы; в срок → 0; 1–3 поздно → −20%; 4+ → −40%.
- hours (actual/budget): ≤0.85 → +20%; 0.85–1.15 → 0; 1.15–1.30 → −20%; >1.30 → −40%.
- multi-foreman: split пропорционально дням в `project_foreman_history`.

**Helpers** (`complete_project`, `main.py:4670`):
- foreman_helper: 30% от primary points.
- installer_helper: 0.

**Punctuality** (`main.py:5402`): +1 форману per worker per day, окно [shift_start − 30m, shift_start + 5m]. UNIQUE на (project, worker, day). НЕ изменена в ребалансе.

**Why:** Артём решил: проектов в OnTime сейчас мало завершённых, но процент S-tier (MG84 Bldg 24-25k) высокий. Поднятые базы делают завершение small-проекта весомым относительно ежедневной дисциплины.

**How to apply:** Применяется только к НОВЫМ `complete_project`. Если попросят пересчитать старые — `DELETE FROM project_scores WHERE project_id IN (...); INSERT` через `compute_points` повторно с теми же `actual_hours/deadline`.

**Frontend mismatch:** `ProjectDetailPage.jsx:38` `computePreview` использует другую формулу (sizeMult = hoursBudget/40, helperPoints=30%, без тиров) — preview расходится с фактическим save. Если станет важно — синхронизировать (или удалить preview, или переписать через compute_points API).
