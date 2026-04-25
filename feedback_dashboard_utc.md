---
name: Dashboard SQL params must be UTC, not local time
description: PostgreSQL `timestamp without time zone` columns store UTC; passing `datetime.now()` silently drops the most recent UTC_offset hours of data
type: feedback
originSessionId: 5926453b-aa53-449f-9edc-92fc5d971f80
---
`real_trades.updated_at` and `simulated_trades.updated_at` are
`timestamp without time zone` storing **UTC** values (verified
2026-04-25). The Postgres server is also UTC.

Server's local timezone is MDT (UTC-6). `datetime.now()` returns naive
local time. Passing it to SQL like `WHERE updated_at < %s` makes
Postgres compare two naive timestamps literally, which silently drops
every row from `[now() - 6h]` to `now()` UTC because their UTC values
are larger than the local-time bound passed in.

Symptom: dashboard's "TOP-10 Winners" missed the 4 most recent
profitable real trades (closed in the last few hours). symbol_count was
17 instead of 22. TP funnel was missing the freshest data.

Fix in `resolve_period()` — use `datetime.utcnow()` instead of
`datetime.now()`. Default ends in `get_strategy_stats` /
`get_top_symbols_by_count` already add `+ timedelta(days=1)` so they
were safe by accident.

**Why:** silent data loss is worse than an error.

**How to apply:** any new SQL bound that compares against
`updated_at` / `created_at` / `entry_time` / `closed_at` MUST use
`datetime.utcnow()` (or a timezone-aware UTC datetime), NEVER
`datetime.now()`. The DB has no timezone awareness; the boundary
between Python and SQL is where mistakes happen.
