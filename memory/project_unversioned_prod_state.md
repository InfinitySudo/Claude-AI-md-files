---
name: Production state not captured by git
description: DB schema changes, Grafana alerts, and systemd units that live only on the VPS — if we rebuild, these must be reapplied manually
type: project
originSessionId: 02a721df-beff-4bfd-bf57-391bd21672c8
---
Several pieces of production state live ONLY on the VPS and are not in the repo. If this project is ever cloned to a fresh machine, these must be re-applied by hand or the bot will silently behave wrong.

## Postgres schema drift (NOT in any migration script)

Applied manually during the 2026-04-11 session:

- `ALTER TABLE simulated_trades ADD COLUMN realized_pnl_usd DOUBLE PRECISION;`
  — total realized PnL including partial TP closures (see `project_realized_pnl_column.md`)
- `ALTER TABLE real_trades ADD COLUMN realized_pnl_usd DOUBLE PRECISION;`
  — symmetry with simulated_trades, though real_trades is currently empty in PAPER mode
- `ALTER TABLE real_trades RENAME COLUMN gross_pnl_pct TO pnl_pct;`
  — matches simulated_trades naming so `get_alltime_stats('real_trades')` doesn't crash

These must be replayed on any new DB before `dashboard_api_v3` or `paper_trading_simulator_v3` will work correctly. The backfill is handled by `src/scripts/backfill_realized_pnl.py` (in repo, idempotent, safe to re-run).

## Grafana alert rule `drawdown-24h` (configured via Grafana API only)

Rule: "Paper drawdown > 20 USD (24h)" in folder `trading-alerts`. Configuration lives in Grafana's internal sqlite (`/var/lib/grafana/grafana.db`), NOT in `/etc/grafana/provisioning/alerting/` — provisioning files weren't used. If Grafana is rebuilt from scratch, the rule must be re-created via `PUT /api/v1/provisioning/alert-rules/drawdown-24h` with the correct body.

Current rule query (after 2026-04-11 fix):
```
SELECT COALESCE(SUM(COALESCE(realized_pnl_usd, gross_pnl_usd)), 0) AS value
FROM simulated_trades
WHERE status='closed' AND exit_time >= NOW() - INTERVAL '24 hours'
```
The previous query used `status='CLOSED'` (uppercase — DB is lowercase) so the rule could never fire. That bug was live from install on 2026-04-10 until 2026-04-11. If you see drawdown alerts "never firing", first check the query for case drift.

## Nginx site config (`/etc/nginx/sites-enabled/dashboard`)

Routes `:8080` → static HTML from `/var/www/dashboard/index.html` and proxies `/api/` → `:8000`. Already documented in `project_deploy_state.md`. Not a git-versioned config — lives only in `/etc/nginx/`.

## `/var/www/dashboard/index.html` is a copy of `TRADING_DASHBOARD.html`

Nginx serves the `/var/www/dashboard/` copy, not the repo file. Deploy flow: `cp /root/4BotsBybit-Trading/TRADING_DASHBOARD.html /var/www/dashboard/index.html`. There's a `deploy_dashboard.sh` script in the repo but the copy can also be done manually. If the Settings tab looks out of date after a `git pull`, the copy wasn't refreshed.

## Systemd units (`/etc/systemd/system/*.service`)

All 5 bot services (`bybit-tradingbot`, `bybit-signalbot`, `bybit-strategy-switcher`, `bybit-control-bot`, `dashboard-api`) are managed by systemd unit files that are NOT in the repo. See `project_deploy_state.md` for the full list.

**How to apply:**
- Before a rebuild/migration: run through this file and make sure every item either has a reproducible path or is re-applied by hand.
- After a `git clone` on a new machine: DB schema + Grafana alert + nginx config + systemd units must be set up before the bots will run correctly.
- When authoring a new "migration script", prefer idempotent SQL in `src/scripts/` (like `backfill_realized_pnl.py`) rather than alembic — the project doesn't use it.
