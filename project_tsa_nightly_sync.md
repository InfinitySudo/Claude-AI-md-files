---
name: TSA nightly legacy-sync
description: Каждую ночь подтягивает отчёты из старого Django+TG-бота в OnTime пока идёт параллельная работа
type: project
originSessionId: 01d3f0af-f97a-467e-bf38-d39ae867510a
---
**Что делает:** `/root/ontime/migration/nightly_sync.sh` — scp свежей `db.sqlite3` с 46.8.227.113 в `/root/ontime/migration/legacy-fresh.db`, потом `sync_legacy.py --from yesterday --to today --apply`. Идемпотентно (проверка `daily_reports` по `user_id+project_id+report_date`).

**Cron:** `30 2 * * *` (02:30 Calgary, до бэкапа `backup.sh` в 03:15). Лог: `/root/ontime/migration/nightly_sync.log`.

**SSH:** ключ `/root/.ssh/id_ed25519.pub` уже прописан на легаси, пароль не нужен.

**Why:** С 2026-04-19 парни работают частично через OnTime, частично через старый TG-бот; план — убить `app-bot` на легаси к ~2026-05-01. До тех пор синхронизация закрывает разрыв.

**How to apply:**
- Проверить после полуночи: `tail /root/ontime/migration/nightly_sync.log`
- Для ручного синка произвольного периода: `python3 sync_legacy.py --from 2026-04-17 --to 2026-04-18 --apply`
- UNMATCHED WORKERS/PROJECTS в логе = человек или объект в легаси, которого нет в OnTime — требует ручного действия (новые именования проектов; появились парни, которых ещё не импортировали).
- Когда выключим TG-бот: удалить cron-строку, архивнуть скрипты в `migration/`, закрыть memory.
