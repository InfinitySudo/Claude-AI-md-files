---
name: stats_mgr._query swallowing INSERTs
description: До 2026-04-29 _query вызывал fetchall() на любой SQL и возвращал [] на ошибке без commit — INSERT/UPDATE тихо откатывались
type: feedback
originSessionId: 5eb329a9-fa6d-4ab4-9f21-be7e401708fa
---
`statistics_manager_v3.py:_query` делал `cur.execute(sql) → fetchall() → return rows`. Для INSERT/UPDATE/DELETE `fetchall()` бросает "no results to fetch" → except → return []. Сам INSERT прошёл, но `conn.commit()` ни разу не вызывался → при возврате connection в pool всё откатывалось.

**Why:** объясняет:
- Blacklist через `add_symbol_to_blacklist` → ничего не появлялось в `symbol_blacklist`
- Любой write через _query (а их в коде много) тихо терялся

**How to apply:** Fixed 2026-04-29 — _query теперь детектит write-команду по verb (INSERT/UPDATE/DELETE без RETURNING) и делает commit, для read остаётся прежнее поведение. Connection-rollback на except для очистки aborted-transaction.

**2026-05-18 — RETURNING leak:** до этой даты ветка `is_write and 'RETURNING' not in sql` молча пропускала DELETE … RETURNING (и INSERT … RETURNING) без commit — UI получал "ok", но транзакция откатывалась. Сломалось `remove_symbol_from_blacklist`: "Remove" в Symbol Blacklist писал removed, символ оставался. Починено: для INSERT/UPDATE/DELETE с RETURNING сначала fetchall, потом commit. Если опять увидишь "API ok, БД не поменялась" — проверь, какой helper делает write.

**Workaround если опять увидишь:** есть `_db_exec` в `dashboard_api_v3.py` (строка 1115) — он коммитит явно. Используй его вместо _query для writes.

**Detection:** `INSERT 0 1` от прямого psql работает, а через бот — нет → _query_swallow.
