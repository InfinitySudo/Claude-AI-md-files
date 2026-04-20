---
name: OnTime email-register upgrades legacy stubs in place
description: При регистрации по email stub-юзер из легаси-импорта апгрейдится, а не создаётся новый
type: feedback
originSessionId: 01d3f0af-f97a-467e-bf38-d39ae867510a
---
При миграции `/root/ontime/migration/import_legacy.py` каждая roster-запись сразу «занимается» stub-юзером: `email='pending+{rid}-tg{tg}@ontime.local'`, `password_hash='!xxx'` (unusable). FKs (`daily_reports`, `work_sessions` и т.д.) привязаны к этому stub-id.

**Why:** Если при регистрации по email INSERT новую строку в `users`, вся история работника (сейчас — 7862 старых отчётов) остаётся у stub-id и теряется связь с реальным юзером. До фикса 2026-04-19 реальные работники получали 409 "This roster entry is already registered" и не могли зарегаться вовсе.

**How to apply:** В `/api/auth/register` (~`main.py:1254`) проверяю `password_hash` начинается с `!` — если да, это stub: делаю `UPDATE users SET email/password/phone/role/full_name WHERE id=stub.id` вместо INSERT. `user_id` сохраняется, все FKs остаются валидными. Роль всегда берётся из `roster.role` — user-picker это подсказка, не источник истины.

`GET /api/auth/bootstrap` отдаёт `has_users / admin_self_register / invite_gated_roles` — LoginPage прячет поле компании и кнопку admin когда юзеры уже есть.

Диагностический SQL: `SELECT COUNT(*) FROM users WHERE password_hash LIKE '!%'` — сколько stubs осталось неупгрейднутыми.
