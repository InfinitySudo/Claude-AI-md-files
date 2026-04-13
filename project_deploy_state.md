---
name: Current deploy state on VPS
description: Which processes run where, ports, nginx config, auth — the live production setup
type: project
originSessionId: 13ab97bb-8dfe-4655-b013-e399065cc3ba
---
## Running processes (VPS)
- **SignalBot**: `python3 src/telegram_bot_runner_v3.py` (from /root/4BotsBybit-Trading)
- **TradingBot**: `python3 src/main_bot_v3.py`
- **StrategySwitcher**: `python3 src/strategy_switcher_v3.py`
- **ControlBot**: managed by systemd `bybit-control-bot.service`, runs from /root/4BotsBybit-Trading
- **Dashboard API**: managed by systemd `dashboard-api.service` on :8000
- **GA Optimizer**: PID 731908 (запущен 2026-04-13)

## Systemd services (all active, restart=always, WorkingDirectory=/root/4BotsBybit-Trading)
- `bybit-control-bot.service` — ControlBot (Telegram management UI)
- `bybit-signalbot.service` — SignalBot (telegram_bot_runner_v3.py, WebSocket scanner)
- `bybit-tradingbot.service` — TradingBot (main_bot_v3.py, order execution)
- `bybit-strategy-switcher.service` — StrategySwitcher (CONS↔TREND)
- `dashboard-api.service` — Dashboard API on :8000
- `trading-api.service` — OLD, STOPPED + DISABLED

## Ports
- **:8080** — nginx → serves HTML from /var/www/dashboard/, proxies /api/ to :8000. **Protected by HTTP Basic Auth** (added 2026-04-13)
- **:8000** — dashboard_api_v3.py (Flask, localhost only via nginx proxy)
- **:3000** — Grafana
- **:9090** — Prometheus, **:9100** — node_exporter

## Authentication (added 2026-04-13)
- **HTTP Basic Auth** на nginx :8080 — covers HTML + all /api/ endpoints
- Credentials: login `artem`, htpasswd file `/etc/nginx/.htpasswd`
- `/health` endpoint open without auth (for monitoring)
- CORS wildcard removed from API proxy
- Before this: dashboard was fully open, anyone could view and modify settings

## Nginx
- Active config: `/etc/nginx/sites-enabled/dashboard`
  - `auth_basic "Trading Dashboard"` + `auth_basic_user_file /etc/nginx/.htpasswd`
  - proxy /api/ → :8000
  - /health → no auth
- Wrestling site: constantwrestling.cloud on :443 (certbot SSL) + :8090 (IP fallback)

## Key state
- **PAPER TRADING mode** — `trading_mode.mode = 'PAPER'`
- Real wallet: ~$17.38 USDT, 0 real open positions
- GA Rank #1 applied 2026-04-13 16:21 — new strategy params in trading_v3_artem.json
- Latest git commit: 971000f (pushed 2026-04-13)

## Parallel agent: OpenClaw Gateway
- `openclaw-gateway.service` (user-level systemd) runs node.js agents on port 18789
- Check before destructive ops on VPS

**Why:** Need to know exact production state to avoid breaking things.
**How to apply:** Before any deploy changes, check this memory for current state.
