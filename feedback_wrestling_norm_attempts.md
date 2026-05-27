---
name: Wrestling norm history schema
description: norm_attempts table + drift in norm_standards (VARCHAR not FLOAT despite CREATE statement)
type: feedback
originSessionId: 349e6fd0-6d83-499e-8c06-b207110cd1c8
---
`norm_attempts(norm_id, athlete_email, club_id, actual_value FLOAT, points_awarded FLOAT, submitted_by, submitted_at)` — добавлена 2026-05-08 чтобы тренер видел прогресс. INSERT в submit_norm + coach_submit_norm обоих эндпоинтах.

**Why:** trainer жаловался что заведённое значение перезаписывает предыдущее и истории нет.

**How to apply:**
- Любая правка эндпоинтов норм должна писать в norm_attempts если меняется actual_value.
- `norm_standards.actual_value` и `target_value` в Postgres = VARCHAR(100), хотя в `CREATE TABLE` стоит FLOAT (drift из старых миграций). Не доверять `CREATE` — всегда `\d norm_standards`.
- В живой БД встречаются non-numeric значения ("best time", "8–15 reps"); фильтр `~ '^-?[0-9]+\.?[0-9]*$'` обязателен в любом backfill / агрегате с приведением к числу.
- backfill идёт из init_db, идемпотентен через LEFT JOIN ... a.id IS NULL.
- UI: `<NormHistory normId>` (src/components/NormHistory.jsx), используется в CoachDashboard + NormsPage.
