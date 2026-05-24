---
name: project-space-live
description: "Trader cockpit — единая Bloomberg/Matrix-стиль панель 4BotsBybit + Gerchik + Copy + GA. Static HTML на :8080. /root/Space_Live, InfinitySudo/Space_Live, deploy → /var/www/dashboard/cockpit.html"
metadata: 
  node_type: memory
  type: project
  originSessionId: eeb6bcbc-09a2-4e37-b01a-7f90d2807f2c
---

**Repo:** `InfinitySudo/Space_Live` (private GitHub) → локально `/root/Space_Live`
**Live:** http://187.77.148.44:8080/cockpit.html (basic auth, nginx :8080, static)
**Stack:** чистый HTML + CSS + canvas, без бандлера. Polling `/api/v2/*` каждые 5 сек.

## Структура
```
public/
  cockpit.html      — главная (terminal-galaxy / matrix-стиль, ~44 KB)
  strategies.html   — drilldown tile-карточки с KPIs
docs/
  mock-a.html       — Variant A · Mission Control (dense grid)
  mock-b.html       — Variant B · Trader Workspace (3-pane IDE)
  mock-c.html       — Variant C · Big Tiles (Apple Health hero)
  mock-d.html       — Variant D · Living Cosmos (первый прототип галактики)
  reference-screen.jpg — референс-скрин от Артёма
```

## Backend endpoints (живут в [[project_dashboard_v2]] 4BotsBybit)
- `/api/v2/overview` — wallet, equity, session_delta
- `/api/v2/strategy/<name>?period=24h` — KPI / open / recent
- `/api/v2/strategy/<name>/rejections` — reject-counters
- `/api/v2/charts/equity?strategy=<name>` — series.{strat}.points[].cum
- `/api/agent-levels` — активные уровни Gerchik

## Эстетика (по референсу)
- Монохром зелёно-серый (Bloomberg/Matrix).
- Чёрная дыра минималистичная: тёмный диск + 2-3 тонких lens-flare слайса.
- Планеты 12-22px, live=зелёные, stale=серые, real-money=оранжевый.
- Тонкие зелёные info-частицы летают между планетами и центром.
- Шрифт mono, тире, ◆-ромбики, ASCII-feel.

## Multi-Galaxy вселенная (с коммита `b5a0d77`, 2026-05-23)
Все 4 галактики активны, switcher работает через select+URL-query:
* **trading.json** — 9 planets: реальные NASA Kepler-параметры (a_au, e, inc_deg, peri_deg), real CONS/TREND/AGGR + Gerchik/Copy + service planets.
* **business.json** — 12 planets: OnTime, Wrestling, Voice/Wife/Son tutors, MAI, Emails-Opt, @solo_claude, @DexClaudCodAIBot, Gerchik, 4Bots (cross-link), Agency.
* **memory.json** — 12 hub-узлов из memory-graph (User Profile, Trading Spec, Hybrid Mode, GA, Dashboard v2, OnTime, Voice Tutor, Wrestling, Bybit 3-Sub, MFE, $10k Strategy, Strict Rules). href → memory-graph/?node=<slug>.
* **deals.json** — snapshot топ-9 real_trades по |PnL|. Класс по исходу: TP1→p-earth, BE→p-venus, SL→p-mars. TODO: dynamic подгрузка из /api/v2/real-trades.

URL routing: `cockpit.html?galaxy=<id>` приоритетнее localStorage.
`?_b=<build>` cache-bust работает на cockpit.html.

## Live wallets & data wiring (с 2026-05-23 коммит `71680f1`)
* COMMAND CENTER · SUB-WALLETS = 3 строки sub1/sub2/sub3 через [[project_wallets_all_endpoint]].
* Deposit/Balance = totals (сумма 3 sub'ов), не sub-1 only.
* LIVE TRADING tile · Deposit = totals.wallet (округлено).
* AI_TRADING_AGENT (Gerchik levels) status-dot: green/red по `/api/agent-levels?status=active count`.
* AI_COPY_TRADING подключён к `/api/v2/gerchik/wallet` + `/api/v2/gerchik/comparison`: PnL, Open, Closed, Eq, top-5 open positions в feed.
* BTC PRICE — публичный Bybit `/v5/market/tickers?symbol=BTCUSDT`, CORS открыт.
* Planet hrefs кликабельны: каждая ведёт в конкретный раздел (CONS/TREND/AGGR → `v2.html?tab=stats&strategy=X`, GA → `?tab=ga`, Gerchik → `agent-levels.html?status=active`, и т.д.).
* `index_v2.html` поддерживает `?tab=X` URL-параметр (коммит `898e018`) — активирует toptab при загрузке.

## Где остановились (session 2026-05-23, коммит `77e17d1`)
**Живая вселенная:** млечный путь (canvas #milkyway, gaussian-belt, 0.55 opacity + screen blend),
чёрная дыра (двойной .bh-void breath 9s/14s + .bh-horizon flicker 5.5s + .bh-core breath 7s +
.lens-spin 120s/200s rotation), галактики дрейфуют через --dx/--dy CSS vars (sin/cos, freq ~1.8e-5 rad/ms).

**Roadmap a-e сделан client-side:**
- a) event-driven FX: `fireFxForNewTrades()` + FX_SEEN set; tick 5s → 3s
- b) `refreshAgentsHealth()` дёргает `/api/agents-health` (graceful 404 → статика)
- c) @media 820px / 540px — accordion-бар сверху, 2/1-колоночный bottom-стек
- d) Sub-3 GERCHIK + Sub-2 COPY tile'ы (`refreshSubTile()`); пробуют `/api/v2/sub/{id}` →
  `/api/v2/sub-balance` → fallback на agent-levels для sub=3; "awaiting endpoint" placeholder
- e) theme switcher matrix/amber/blue через `:root[data-theme]` + localStorage persist

## Что ещё в очереди (нужен бэкенд в 4BotsBybit dashboard-api)
- `/api/agents-health` — реальные heartbeat'ы systemd для AGENTS-списка
- `/api/v2/sub/2`, `/api/v2/sub/3` — balance/open/recent для SUB-2/SUB-3 tile'ов
- WebSocket/SSE → push-уведомления (текущий polling 3s — компромисс)

## Связано
- [[project_dashboard_v2]] — источник API для cockpit
- [[project_gerchik_bot]] — Sub-3 планета
- [[project_bybit_3sub_architecture]] — 3 sub-аккаунта (TradingBot/Copy/Gerchik)
