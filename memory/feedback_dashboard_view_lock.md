---
name: Dashboard 502 от чужой idle-in-transaction
description: Dashboard-api виснет на старте если другой бот держит idle-in-transaction lock на real_trades_compat; защищено двумя слоями
type: feedback
originSessionId: 93067773-cafa-4ab3-b8c6-cf84bdc85eda
---
При рестарте `dashboard-api` 502 возвращался часами потому что `_ensure_real_trades_compat_view()` делает `DROP VIEW IF EXISTS real_trades_compat`, а другой бот (например `strategy_switcher_v3`) оставлял `idle in transaction` на коннекте, который читал ту же view → AccessShareLock держится бесконечно → DROP блокируется → `app.run()` никогда не вызывается → порт 8000 не байндится.

**Why:** systemctl показывает `active (running)` потому что Python-процесс жив, но висит в do_poll на сокете к Postgres до StatsManager-init. Снаружи это выглядит как 502 от nginx :8080 → :8000.

**How to apply:**

Защита в два слоя (2026-05-09):

1. **Postgres-level**: `ALTER ROLE trading_bot SET idle_in_transaction_session_timeout = '60s';` — любой забытый txn умирает за минуту, влияет только на новые коннекты.

2. **Script-level**: `REAL_TRADES_COMPAT_VIEW_SQL` начинается с `SET LOCAL lock_timeout = '5s';`, а `_ensure_real_trades_compat_view()` ловит exception и логает warning без re-raise → старая view используется и dashboard всё равно поднимается.

Диагностика рецидива:
```sql
-- кто держит idle-in-transaction
SELECT pid, application_name, state, NOW()-xact_start AS held, LEFT(query,80)
FROM pg_stat_activity
WHERE datname='trading_bot_v3' AND state='idle in transaction'
ORDER BY xact_start;

-- ungranted locks
SELECT pid, mode, locktype, relation::regclass, granted
FROM pg_locks WHERE NOT granted;
```

`pg_cancel_backend(pid)` НЕ помогает на `idle in transaction` (нет активного query) — нужен `pg_terminate_backend(pid)`.

Если 502 вернётся: проверить (1) есть ли idle-in-tx, (2) процесс dashboard висит ли в `do_poll` на 5432-й. Если оба «да» — terminate backend; код уже сам через 5s прервётся, но если SET не доехал (старый бинарник) — terminate спасает.

Связанные файлы: `src/dashboard_api_v3.py:5224` (REAL_TRADES_COMPAT_VIEW_SQL), `:5250` (_ensure_real_trades_compat_view).
