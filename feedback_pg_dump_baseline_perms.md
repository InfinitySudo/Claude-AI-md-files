---
name: pg-dump-baseline-tables-require-grant-to-non-postgres-role
description: "db-backup сервис тихо клал zero-byte dumps 4 дня потому что pg_dump as `trading_bot` user не мог LOCK TABLE на `*_baseline_v3_snapshot` / `*_archive_*` tables owned by postgres. systemd показывал failed, никто не смотрел."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f4c4861-fd60-4f57-b7af-c4260e03075c
---

Любой `pg_dump` запускающийся от **не-postgres role** требует SELECT на ВСЕ таблицы в schema иначе `LOCK TABLE ... IN ACCESS SHARE MODE` падает с `permission denied for table X` для tables owned кем-то другим. Output file создаётся пустой (0 bytes), exit code 3.

**Fix (one-time admin task):**
```sql
-- Run as postgres superuser
GRANT SELECT ON ALL TABLES IN SCHEMA public TO trading_bot;
GRANT SELECT, USAGE ON ALL SEQUENCES IN SCHEMA public TO trading_bot;
-- Future tables created in this schema:
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO trading_bot;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, USAGE ON SEQUENCES TO trading_bot;
```

**Why:** 2026-05-15 — `bybit-db-backup.service` failed 4 дня подряд после baseline migrations создавших `simulated_trades_baseline_v3_snapshot` и `*_archive_*` tables owned by `postgres` (не `trading_bot`). pg_dump partial-output exited code 3, dump files на диске 0 bytes. Systemd показывал failed но никто не проверял — backup'ов фактически не было.

**How to apply:**
- При добавлении новых tables в production DB → проверить какой owner. Если не основной user — `GRANT SELECT TO <backup_user>` сразу
- Periodic smoke: `ls -la /tmp/<db>_backups/` — пустые файлы = red flag
- Manual sanity: `pg_dump --host=... --user=<backup_user> -Fc ... > /tmp/test.dump && ls -la /tmp/test.dump` должен быть >> 0 bytes
- В `db_backup.py` имеет смысл добавить validation: после dump проверить `os.path.getsize(out_file) > 1024` иначе raise — сейчас успешно завершает на partial output

Связано: [[project_unversioned_prod_state]], [[feedback_real_trades_truth]].
