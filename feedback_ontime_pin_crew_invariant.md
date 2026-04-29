---
name: OnTime Pin Crew Invariant
description: project_installers надо считать source-of-truth для крю; legacy-импорт его не заполнил, авто-pin в /api/reports + backfill закрывают дыру
type: feedback
originSessionId: 3d0b2070-3ff3-4cd8-8c27-f6eddc76ef8e
---
`project_installers` (+ `projects.foreman_id`) — единственный source of truth для «кто закреплён за проектом». Любой счётчик «крю на объектах» (digest, dashboards, dropdowns) должен ходить через эти таблицы, а не через `daily_reports`.

**Why:** legacy-импорт 2026-04-17 принёс отчёты, но НЕ принёс crew assignments. Из-за этого 38 человек реально работали, но pinned было 22. Артем заметил несоответствие в digest 2026-04-29.

**How to apply:**
- Digest и подобные счётчики используют `status IN ('active','in_progress','overdue')` — overdue = «работаем, но deadline прошёл», крю там есть.
- Auto-pin hook в `POST /api/reports` (main.py:4320) — `INSERT OR IGNORE` если reporter не management и не foreman_id этого проекта.
- При появлении новых orphan-проектов (status active/overdue, 0 в project_installers, но есть recent daily_reports) — прогоняй backfill: `INSERT OR IGNORE INTO project_installers SELECT DISTINCT project_id, user_id, 1 FROM daily_reports WHERE report_date >= date('now','-14 days') AND ...`.
- НЕ доверяй `daily_reports` как источнику pinned crew для UI — он вторичен. Pin'инг → отчёты, не наоборот (но мы добавили self-heal, чтобы дыры залатывались сами).
