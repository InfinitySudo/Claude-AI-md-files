---
name: Current deploy state on VPS
description: Which services run where, ports, nginx routing, project directories — live production setup as of 2026-04-30 post-reboot
type: project
originSessionId: a86c82dd-a6d1-4564-8fcb-d5685124b663
---
## Running services (systemd, all enabled+active)

### Trading stack (`/root/4BotsBybit-Trading`)
- `bybit-signalbot` — telegram_bot_runner_v3 + WS scanner
- `bybit-tradingbot` — main_bot_v3 + order execution
- `bybit-control-bot` — Telegram management UI
- `bybit-strategy-switcher` — CONS↔TREND hourly check
- `dashboard-api` — Flask API на :8000

### OnTime (`/root/ontime`)
- `ontime-api` — FastAPI uvicorn :8002 (127.0.0.1 only)
- `ontime-bot` — Telegram bot

### Wrestling (`/root/Wrestling-Performance-Tracker`)
- `wrestling-api` — FastAPI :8001

### Telegram-bots
- `claude-telegram-bot` (`/root/claude-telegram-bot`) — Anthropic API bridge
- `celpip-bot@artem` + `celpip-bot@liliia` (`/root/English-Teacher-CELPIP`)
- `solo-claude-approve` (`/root/solo_claude_bot`) — draft approval listener

### Infrastructure
- `nginx`, `postgresql@16-main`, `docker`, `grafana-server`,
  `prometheus`, `prometheus-node-exporter`, `ssh`

## Listening ports

| Port | Process | Notes |
|------|---------|-------|
| 22   | sshd    | |
| 80   | nginx   | HTTP (redirects/Certbot) |
| 443  | nginx   | HTTPS (ontime.management, constantwrestling.cloud) |
| 3000 | grafana | |
| 5432 | postgres | localhost |
| 8000 | dashboard-api | Flask, exposed (но фронт через 8080 nginx) |
| 8001 | wrestling-api | FastAPI |
| 8002 | ontime-api    | FastAPI, localhost only |
| 8080 | nginx → :8000 | Trading dashboard, HTTP Basic Auth |
| 8090 | nginx → :8001 | Wrestling alt port |
| 8443 | nginx → :8001 | Wrestling SSL alt port |
| 9090 | prometheus | |
| 9100 | node_exporter | |
| 18789, 18791 | openclaw-gateway | parallel agent — НЕ трогать |

## Nginx sites (`/etc/nginx/sites-enabled/`)

- **`dashboard`** :8080 → root `/var/www/dashboard`, `/api/` → :8000.
  HTTP Basic Auth `artem` / htpasswd at `/etc/nginx/.htpasswd`.
- **`ontime`** ontime.management :443 (Certbot) → root `/root/ontime/dist`,
  `/api/` → :8002.
- **`wrestling`** constantwrestling.cloud :443 (Certbot) + :8090/:8443 →
  root `/root/Wrestling-Performance-Tracker/dist`, `/api/` → :8001.

## Trading state (live снимок)

- Hybrid mode: `global=PAPER`, `per_strategy={CONS:PAPER, TREND:REAL,
  AGGRESSIVE:REAL}` — см. `project_hybrid_mode.md`.
- `strategy_mode=AUTO`, `forced_strategy=CONSERVATIVE` →
  `effective_route=PAPER` сейчас.
- Soft-gate scorecard verdict: **STOP** (fail_count=3,
  recommend_pause=false). См. `project_trading_state_softgate.md`.
- Daily DD 3.19% / weekly 13.04% / total 0% — пороги 5/15/15%.
- Bybit mainnet, 0 open позиций, wallet требует свежей проверки
  (см. `feedback_real_trades_truth.md` — DB лжёт про PnL, всегда
  через `get_bybit_realized_pnl()`).

## Dashboard pages (split с 2026-04-23)

- `/` или `/index.html` → 📒 PAPER view
- `/real.html` → 💰 REAL view
- См. `project_dashboard_split.md`, `project_dashboard_apply_chain.md`.

## GA optimizer

- Последний run: `ga-optimizer-1777498652.service`
  (started 2026-04-29 15:37 UTC, completed 2026-04-30 04:10).
- Запускать через systemd-run --unit --slice, **не** Popen — см.
  `feedback_ga_subprocess_detach.md`.
- Walk-forward 70/30 split активен — см. `project_ga_walk_forward_todo.md`.

## Disabled orphans (НЕ восстанавливать)

- `bybit-dashboard-8080.service` — disabled 2026-04-30 после reboot.
  Ссылался на `/root/4botsBybit-production` (не существует),
  спамил журнал каждые 10s. Порт 8080 теперь у nginx.

## Where state drifts

- DB schema, Grafana dashboards, nginx, /var/www, .env, Certbot certs
  — не в git. См. `project_unversioned_prod_state.md`.
- Repo mirrors HTML: `TRADING_DASHBOARD.html` (paper),
  `TRADING_DASHBOARD_REAL.html` (real).
- Каждый сервис своя venv внутри своей `WorkingDirectory`.

## Parallel agent

- OpenClaw Gateway (`openclaw-gateway`, port 18789/18791) — node.js
  агенты на той же VPS. Перед destructive ops проверять нет ли его
  процессов. См. `feedback_parallel_agents.md`.

**Why:** один источник правды по тому, что реально крутится. Без него
после reboot/migration легко пропустить orphan-юнит или сломать
nginx-маршрут чужого проекта.

**How to apply:** перед любым deploy/restart/migration читать этот
файл, потом сверяться с `systemctl list-units --state=active` и
`ss -tlnp` — drift между этой памятью и реальностью обновлять сразу.
