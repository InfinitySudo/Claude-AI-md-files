---
name: project_tsa_worker_material_breakdown
description: "OnTime Team activity — клик по работнику = разбивка установленных материалов, время, % бюджета + лидерборд per-material с окнами дат"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5b904a97-9e9f-4dd3-8802-6c3fef431230
---

OnTime: в панели **Team activity** на странице объекта (`TeamHistoryPanel.jsx`) строки работников кликабельны → модалка `WorkerBreakdownModal.jsx` с разбивкой по этому работнику на этом объекте.

**Что показывает:** какие материалы установил (qty / план BOM), оценка времени на каждый материал, $-стоимость, % от контракта / от установленного всеми, % от плана. Внутри — лидерборд per-material «кто больше установил» с окнами day/week/month/project. Сверху селектор периода: **От начала объекта / Неделя / Месяц ▾** (список месяцев из ответа).

**Backend (`backend/main.py`, рядом с `project_team_history` ~line 5128):**
- `GET /api/projects/{pid}/team/{uid}/material-breakdown?period=project|week|month&month=YYYY-MM` — селектор периода в модалке: От начала объекта / Неделя / Месяц▾ (список месяцев из ответа `months`). Окно фильтрует вклад работника И знаменатели (project_qty, installed_value); фикс-цели плана НЕ урезаются.
- `GET /api/projects/{pid}/materials/{mid}/leaderboard?period=day|week|month|project&scope=project|company`

**Ключевые решения:**
- Время per-material = ОЦЕНКА: дневные часы из `daily_reports.hours` распределяются по материалам дня пропорционально $-стоимости (OnTime пишет часы за день, не за материал).
- Canonical/alias: install засчитывается плановому материалу P если `dri.material_id = P OR canonical_id = P` — как в `project_budget` (НЕ роллапить install вверх к своему canonical, иначе отрыв от плана — была эта ошибка). См. [[feedback_ontime_canonical_id]].
- Окно дат фильтрует и вклад работника, и знаменатели (project_qty, installed_value); фикс-цели плана/контракта НЕ урезаются.
- `$`/wage только finance-роли (`_has_finance_view`); installer → 403. `pct_of_plan` пуст когда `planned_qty` не задан — UI откатывается на `pct_of_project_qty` (доля от установленного).

Связано: [[project_tsa_daily_reports]], [[project_ontime_wage_cost]], [[project_tsa_timeline]].
