---
name: OnTime Scoring (points)
description: Тиры + financial loss-gate (2026-04-29) + foreman-only rule (2026-04-30) — баллы только role=foreman
type: project
originSessionId: 2698e6df-f89c-4d5c-ae55-ba7c1be6f1d9
---
**TIER_BASE** (после ребаланса 2026-04-27):
- S (≤$25k): **250**
- M ($25–50k): **500**
- L ($50–100k): **1000**
- XL (>$100k): **2000**

Старые базы (50/150/350/700) проигрывали punctuality: Igor с 16 рабочими = 352 punctuality/мес против 65 за S-проект — 1 проект ≈ 4 дня дисциплины.

**Формула** (`compute_points`, `main.py:2791`):
- **Loss gate (2026-04-29)**: если `financial_result < 0` (любой убыток) → **points = 0**, независимо от hours/deadline. Артём: foreman не справился с задачей если убыток, баллы не должны начисляться. При деплое обнулено 6 исторических score-rows по 5 убыточным проектам (Sage Walk Bldg 2 −$47k, Pinegate −$23k, Logel Brick −$7k, Sage Walk MASONRY −$5k, ATCO Bldg B −$3k); previous_points сохранены в breakdown_json.
- Иначе: `points = max(0, base + deadline_adj + hours_adj)`
- deadline: ≥10 дней раньше → +30% базы; в срок → 0; 1–3 поздно → −20%; 4+ → −40%.
- hours (actual/budget): ≤0.85 → +20%; 0.85–1.15 → 0; 1.15–1.30 → −20%; >1.30 → −40%.
- multi-foreman: split пропорционально дням в `project_foreman_history`.

**Financial result source**: `complete_project` тянет `result` через `enrich_project(include_money=True)` — тот же расчёт что на dashboard (`min(earned, budget) − salary` с wage_history). breakdown_json сохраняет `financial_result`, `financial_zero`, `previous_points`.

**Recompute script**: `backend/recompute_loss_scores.py` — one-shot для backfill после изменения логики; обнуляет project_scores где result<0.

**Helpers** (`complete_project`, `main.py:4670`):
- foreman_helper: 30% от primary points — **ТОЛЬКО если user.role='foreman'** (rule 2026-04-30).
- installer_helper: 0.
- POST `/api/projects/{pid}/helpers` отказывает 400 если role=foreman_helper, а user.role≠foreman.

**Foreman-only primary rule (2026-04-30):** в complete_project spans
фильтруются по `users.role='foreman'` — installer'ы и helpers в
project_foreman_history не получают долю points (legacy 2026-04-17 import
загнал installer'ов как primary, Igor Kurinnye терял 71pt каждому
Dmytro Kurinnyi на MG84 builds). Если на проекте все spans non-foreman →
никто не получает баллов. Backfill для existing data:
`backend/recompute_foreman_only_scores.py` (отработал на 9 проектах
2026-04-30; +71+71 Igor Kurinnye на MG84 Bldg 17 + Bldg 2).

**Punctuality** (`main.py:5402`): +1 форману per worker per day, окно [shift_start − 30m, shift_start + 5m]. UNIQUE на (project, worker, day). НЕ изменена в ребалансе.

**Why:** Артём решил: проектов в OnTime сейчас мало завершённых, но процент S-tier (MG84 Bldg 24-25k) высокий. Поднятые базы делают завершение small-проекта весомым относительно ежедневной дисциплины.

**How to apply:** Применяется только к НОВЫМ `complete_project`. Если попросят пересчитать старые — `DELETE FROM project_scores WHERE project_id IN (...); INSERT` через `compute_points` повторно с теми же `actual_hours/deadline`.

**Frontend mismatch:** `ProjectDetailPage.jsx:38` `computePreview` использует другую формулу (sizeMult = hoursBudget/40, helperPoints=30%, без тиров) — preview расходится с фактическим save. Если станет важно — синхронизировать (или удалить preview, или переписать через compute_points API).
