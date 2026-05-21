---
name: session-2026-05-19-ontime-polish
description: "OnTime UX polish + accounting fixes session — 9 features pushed, key invariants for crew planning, billing hours, address links"
metadata: 
  node_type: memory
  type: project
  originSessionId: c6b18e92-8a2c-429c-bf02-2de5a08fc207
---

OnTime session 2026-05-19 — 9 коммитов, frontend + backend (`/root/ontime`).

**TL;DR:** OT-panel filter+sort + green-pulse working-now indicator + clickable address (только на ProjectDetailPage), planning crew теперь учитывает регулярных гостей, hours-per-day кликабельный popup, lunch+9h cap для live sessions, backfill missing reports, service-task timer, delivery может регистрировать lifts + одноразовые заправки.

**Surprising / non-obvious bits worth keeping:**

- **OT-panel `slice(0,8)` был визуальной заглушкой**, не счётчиком чекинов — Артём думал «сегодня чекинились только 8». Сейчас: full table в `max-h-64` со sticky thead + filter + sort by pp_hours desc.
- **Address-link в списке проектов = ловушка.** Из-за `target=_blank` Igor K на Android в PWA уносит на Google Maps вместо открытия проекта. Кликабельный адрес теперь **только** на `ProjectDetailPage` (с иконкой MapPin), в `ProjectsPage`/`InstallerHomePage` — plain text. См. [[feedback_react_select_fallback]] / [[feedback_ontime_foreman_mobile_actions]] для аналогичных гетч.
- **`_calc_crew_budget` (main.py:3391)** теперь объединяет `registered_crew` (foreman + project_installers + project_helpers) с `_recent_project_workers(project_id, window=7, min_days=2)` — гости-регулярные тоже считаются. Pace req / Crew gap / Suggested crew стали реалистичными. Response теперь включает `registered_crew_size / ghost_crew_size / ghost_workers` для UI чипа.
- **Open-session minutes раньше билились сырыми** (`now − started_at`), без lunch и без cap. Создан `_open_session_billable_minutes(started_at, now_dt)` — вычитает 12:00-12:30 + cap `WORKDAY_HOURS × 60`. `_session_minutes_safe` и `_ts_session_minutes` оба идут через него.
- **Service task quick check-in:** `work_sessions.service_task_id` (миграция). `POST /api/service-tasks/{id}/start-work` закрывает другие открытые сессии юзера и открывает новую; `/stop-work` через `_close_session` (lunch+cap применяются) + накапливает `service_work_hours`. В `/api/timesheet/by-allocation` сессии с `service_task_id IS NOT NULL` исключены из 'project' group → нет двойного счёта.
- **Backfill missing reports:** `POST /api/reports` всегда принимал любую `report_date` (не only today), crew-guard уже пускал по session-bypass за последние 14 дней. Не хватало только UI: `GET /api/me/pending-reports` (≥30min session, no report за тот день) + амбер блок на `InstallerHomePage`. `ReportPage` уже понимал `?project_id=X&date=YYYY-MM-DD`.
- **External refuels = отдельная таблица** (`external_refuels`), НЕ NULL в `lift_refuels.lift_id`. Кто заправляет чужую технику — пишет туда. Видно в Lifts page отдельной карточкой с total month L/$.
- **Delivery + service теперь могут регистрировать lifts** (`require_lift_register` = LIFT_MANAGER ∪ delivery ∪ service). Hard delete остался admin-only. Frontend через `canRegisterLifts`.
- **`AllocationView` зелёная пульсирующая точка** = открытая `work_session` на этом конкретном проекте; backend отдаёт `active_now` per worker; такие сортируются наверх блока.
- **Hours-per-day bar теперь кликабельный** → `DayDetailModal` (через `GET /api/projects/{pid}/day-detail`) показывает per-worker breakdown с интервалами сессий. Labels часов перенесены ВНУТРЬ столбика (top-0.5, белый с drop-shadow) чтобы не обрезались.

**Гетчи которые я наступил и зафиксил по ходу:**
- **Hooks-order** в `TaskDetailModal` — добавил `useState`/`useEffect` для таймера ПОСЛЕ `if (!task) return null` → blank screen. Поднял выше early-return. Ср. [[feedback_react_hooks_order]].
- **`inline-flex + truncate`** в `AddressLink` без width-bounded parent просто расширяло страницу. Заменил на `block + min-w-0 + break-words`.

**Коммиты (порядок):** 7cc5b74, b27e3b4, dbb3a84, 68ab816, f4c51f5, 1590b2f, 834badf, 7f9b5ec, 6a6d8ef, a3f78e9, aecfa0c, 6b7d182, 5b69643. См. `git log --since=2026-05-19` в `/root/ontime`.

Linked: [[project_tsa_timeline]] [[project_tsa_timesheet]] [[project_ontime_heartbeat]] [[project_ontime_wage_cost]] [[feedback_billable_hours_dedup]] [[feedback_ontime_pin_crew_invariant]] [[feedback_react_hooks_order]]
