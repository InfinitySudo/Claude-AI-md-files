---
name: Dashboard Settings tab architecture
description: How the dashboard's Settings tab is wired up — endpoints, registry, confirm phrases, dual-writer invariant with ControlBot
type: project
originSessionId: 02a721df-beff-4bfd-bf57-391bd21672c8
---
The dashboard at `http://187.77.148.44:8080/` has TWO tabs: `📊 Dashboard` and `⚙️ Settings`. The Settings tab is a full mirror of ControlBot's Telegram UI — every operator knob is editable from the browser (added 2026-04-11). **ControlBot Telegram and the dashboard are two parallel writers into the same storage**, so changes from either surface are visible to both.

**Why it exists:** Artem found the Telegram UI clunky and asked for everything to be available in the browser, with REAL-trading protected by a confirm phrase.

**Backend (`src/dashboard_api_v3.py`):**
- `SETTINGS_REGISTRY` dict (~line 400) is the **single source of truth** — every knob has: key, category, label, backend (`db`|`trading_json`|`signal_json`), kind, min/max/enum, restart requirement, hint. If you add a new ControlBot command, add it here and both GET/POST endpoints handle it automatically.
- Storage backends: `bot_settings` Postgres table, `config/trading_v3_artem.json`, `signal_bot_config.json`.
- JSON writes use `fcntl.flock` + temp-file rename (`_read_json_atomic` / `_write_json_atomic`). Never bypass this — ControlBot Telegram writes the same files concurrently.
- DB writes use `_db_exec()` helper (NOT `stats_mgr._query()` — that one `fetchall()`s and crashes on INSERT).

**Endpoints added:**
- `GET /api/settings` — snapshot (20 settings + operational state)
- `POST /api/settings/<key>` — body `{value}`, validates, routes to correct backend
- `GET /api/services` — `systemctl is-active` for 5 services
- `POST /api/services/<svc>/<action>` — allowlist `{bybit-tradingbot, bybit-signalbot, bybit-strategy-switcher, bybit-control-bot, dashboard-api}` × `{start, stop, restart, status}`
- `POST /api/mode/switch` — PAPER↔REAL with audit log, auto-restarts bybit-tradingbot
- `GET /api/logs/<service>?lines=N` — journalctl tail, max 1000 lines
- `GET /api/export/trades.csv?period=24h|7d|30d|all` — CSV with `realized_pnl_usd`
- `POST /api/update-code` — git pull, refuses if dirty, does NOT auto-restart
- `POST /api/clean-database` — TRUNCATEs 14 tables, preserves `bot_settings` and `current_strategy`

**Confirm phrases (exact match required in request body):**
- REAL trading: `I UNDERSTAND REAL MONEY`
- Update Code: `UPDATE CODE`
- Clean Database: `DELETE ALL DATA`

**Frontend (`TRADING_DASHBOARD.html`):**
- Tab switcher toggles `#dashboard-view` / `#settings-view` display. Charts are NOT destroyed on tab change — they survive hidden.
- Generic `openPhraseModal(opts)` helper used by Update Code and Clean DB — reusable for future destructive actions.
- Settings fields render per-category from `data-fields-for="<cat>"` containers. Field changes trigger immediate POST — inline status shows `saving...` → `✓ saved` or `✗ error`. Fields with `requires_restart` show an `⚠ restart <service>` badge; hot-reload ones show `⚡ hot`.

**How to apply:**
- Before touching any settings mutation in ControlBot, remember the dashboard writes the same files/DB — both must stay in sync. Prefer adding new knobs to `SETTINGS_REGISTRY` first, then wiring ControlBot to route through the same helpers.
- When adding a new setting: pick backend (db preferred for hot-reload), add registry entry with validation, no frontend changes needed — it appears automatically under its category section.
- Do not remove the flock — concurrent writes from Telegram and browser will tear the JSON otherwise.
- `bot_settings` and `current_strategy` are the **persistence boundary**: clean-database intentionally spares them. If you change that invariant, StrategySwitcher will restart from an empty state on next boot.
