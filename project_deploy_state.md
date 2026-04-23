---
name: Current deploy state on VPS
description: Which processes run where, ports, nginx config, auth, hybrid trading mode — the live production setup as of 2026-04-23
type: project
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
## Running processes (VPS)
- **SignalBot** — `bybit-signalbot.service` (telegram_bot_runner_v3.py +
  WebSocket scanner)
- **TradingBot** — `bybit-tradingbot.service` (main_bot_v3.py + order
  execution)
- **StrategySwitcher** — `bybit-strategy-switcher.service` (CONS↔TREND
  hourly check); currently in MANUAL mode
- **ControlBot** — `bybit-control-bot.service` (Telegram management UI)
- **Dashboard API** — `dashboard-api.service` on :8000

## Ports / nginx
- **:8080** — nginx → serves HTML from `/var/www/dashboard/`, proxies
  `/api/` to :8000. **HTTP Basic Auth** (login `artem`,
  htpasswd at `/etc/nginx/.htpasswd`).
- **:8000** — dashboard_api_v3.py (Flask, localhost only via nginx).
- **:3000** — Grafana, **:9090** Prometheus, **:9100** node_exporter.

## Dashboard pages (split 2026-04-23)
- `/` (or `/index.html`) → 📒 PAPER view (default)
- `/real.html` → 💰 REAL view
- Top nav switches between them. See `project_dashboard_split.md`.

## Trading mode (hybrid since 2026-04-23)
- `trading_mode.mode = 'PAPER'` (global fallback)
- `trading_mode.per_strategy = {CONSERVATIVE: PAPER, TREND: REAL,
   AGGRESSIVE: REAL}` overrides per signal
- `current_strategy = TREND` (DB), `strategy_mode = MANUAL`
- See `project_hybrid_mode.md` and `feedback_paper_vs_real.md`.

## Bybit account
- Mainnet, IP whitelist: VPS 46.8.232.182 + Артёмов 187.77.148.44
- API permissions: ContractTrade Order+Position, DerivativesTrade
  (readOnly=0)
- **Wallet $200.92 USDT** (Артём пополнил с $100.38 → $200.92 на
  2026-04-23)
- 0 open positions on exchange (как на момент enabling hybrid)
- Risk per trade: $1 across all strategies (cons/trend/aggr all = $1)
- max_concurrent_positions: 100 (drawdown guard 10%/day per strategy is
  the actual safety net, see `project_hybrid_mode.md`)

## GA optimizer state
- **GA run #2 in progress** since 2026-04-22 22:40 UTC (started after
  the detach fix). PID 2240633, **detached process group** so survives
  service restarts. Notify watcher PID separate, also detached.
- ETA ~24h to finish.
- Dashboard `/api/ga/status` reports running until completion.
- After finish: `ga_results_latest.json` will overwrite. Apply
  decision deferred until I review.

## Where state can drift
- DB schema, Grafana dashboards, nginx, /var/www, .env — not in git
  (see `project_unversioned_prod_state.md`).
- Repo mirrors of dashboard HTML: `TRADING_DASHBOARD.html` (paper),
  `TRADING_DASHBOARD_REAL.html` (real).
- Active PID files: `data/ga_status.json` (GA process meta).

## Parallel agent
- OpenClaw Gateway (`openclaw-gateway.service`, port 18789) runs
  node.js agents on the same VPS — check before any destructive
  operation. See `feedback_parallel_agents.md`.

**Why:** Knowing the exact production state prevents breaking things.
Hybrid mode + real money + live GA all in flight as of this commit.

**How to apply:** Before any deploy/restart/config change:
1. Check this memory for what's running.
2. Verify wallet & open positions if touching trading path.
3. If restarting dashboard-api or signalbot/tradingbot, ensure
   subprocesses (GA) are detached or check that nothing important is
   in flight.
