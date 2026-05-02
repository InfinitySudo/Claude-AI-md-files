---
name: TSA Legacy server (46.8.227.113)
description: Старый Django+TG-бот сервер TSA, откуда мигрировали данные в OnTime 2026-04-17
type: project
originSessionId: 7307290c-93f4-4995-a318-269609a49e02
---
**Сервер:** 46.8.227.113 (Ubuntu 24.04, отдельный VPS)
**Что крутится:** Docker-compose стек: `app-web` (Django/gunicorn), `app-bot` (aiogram TG-бот), `app-celery`, `app-celery_beat`, `app-nginx`, `app-redis`. Путь: `/home/app/`.
**БД:** SQLite `/home/app/db/db.sqlite3` (2.2 MB). `/home/app/TSA/db.sqlite3` — пустой, не путать.

**Что оттуда импортировали в OnTime 2026-04-17:**
- 91 материал (merge по имени, цены обновлены)
- 69 работников → 27 новых roster + stub users, 42 уже были в сиде
- 59 проектов (20 активных, 39 архивных по `is_archived`)
- 558 связей project↔material (без planned_qty — нет в старой схеме)
- 7862 из 7909 отчётов → `daily_reports` + 16807 `daily_report_items` (144 items пропущено из-за несовпадения имён материалов)

**Why:** Старая система (Django + TG-бот + Google Sheets для расчётов) заменяется OnTime. План: 2-3 недели параллельная работа (до ~2026-05-08), потом вырубить `app-bot` через `docker compose stop bot` на 46.8.227.113.

**How to apply:**
- Скрипт импорта одноразовый: `/root/ontime/migration/import_legacy.py`. Копия старой БД: `/root/ontime/migration/legacy.db`.
- Перед повторным запуском — не запускать без чистки, создаст дубли (idempotency не реализована).
- Старые credentials засвечены в чате 2026-04-17 → Артёма предупредил, надо сменить root/user пароли на 46.8.227.113.
