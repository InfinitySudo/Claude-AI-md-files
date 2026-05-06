---
name: Dashboard v1 vs v2 — don't confuse
description: Two dashboards live in parallel until v2 polished; editing the wrong one or the wrong layer (repo vs deploy) silently breaks prod
type: feedback
originSessionId: adfb2918-d7eb-454d-8326-11f044ee5979
---
С 2026-05-05 в проде ОДНОВРЕМЕННО работают две версии дашборда. До команды Артёма «cutover» обе live, обе нужны.

**Why:** v2 ещё в полировке. Артём кликает между ними через switcher (правый верх). Если я сломаю одну — потеряет рабочий инструмент посреди торговли.

**How to apply:**

При любой правке дашборда сначала скажи себе вслух «v1 или v2?», потом редактируй. Не правь обе сразу «чтобы синхронизировать» — у них разная архитектура и разные источники данных.

## Карта файлов

| Версия | URL | Source-of-truth | Deploy target | Endpoints |
|---|---|---|---|---|
| **v1** | `/` | `/root/4BotsBybit-Trading/TRADING_DASHBOARD.html` | `/var/www/dashboard/index.html` (cp via `scripts/deploy_dashboard.sh`) | `/api/trader-stats?source=paper` (1 mega-endpoint), `/api/symbol-breakdown`, `/api/funnel-history` |
| **v2** | `/v2.html` | `/root/4BotsBybit-Trading/index_v2.html` | `/var/www/dashboard/v2.html` (просто `cp`) | `/api/v2/{overview,strategy/<n>,per-symbol,charts/{equity,distribution,hour-heatmap,comparison}}` + большинство существующих |

**Никогда не редактируй файлы в `/var/www/dashboard/` напрямую** — они перезаписываются deploy-скриптом. Правь source в `/root/4BotsBybit-Trading/`, потом deploy.

## Как опознать v1 vs v2 при чтении кода

- v1 (TRADING_DASHBOARD.html, ~4470 строк): класс `tab-bar`, `data-tab="dashboard"`, `data-tab="settings"` (только 2 таба), констант `DASHBOARD_SOURCE`, цвет акцента `#4a9eff`
- v2 (index_v2.html, ~1700 строк): класс `toptab`, `data-toptab="stats|charts|control|ga|symbols|settings"` (6 табов), Chart.js CDN, классы `strategy-card paper/real/paper_pending_real`, цвет акцента `#2563eb`

В обоих файлах есть одинаковый switcher `class="dash-switcher"` (v2) / `class="dash-switcher-v1"` (v1) в правом верхнем углу — игнорируй его при оценке версии.

## Endpoints — что общее, что v2-only

**v2-only (трогать осторожно — frontend v2 на них завязан):**
`/api/v2/overview`, `/api/v2/strategy/<n>`, `/api/v2/per-symbol`,
`/api/v2/charts/{equity,distribution,hour-heatmap,comparison}`.

**Общие (v1+v2 оба используют):**
`/api/settings`, `/api/settings/<k>`, `/api/services`, `/api/services/<svc>/<action>`,
`/api/trading-state`, `/api/trading-state/{pause,resume}`, `/api/mode/switch`,
`/api/scorecard`, `/api/funnel-history`, `/api/dd/ack-session-start`,
`/api/blacklist`, `/api/blacklist/<sym>`, `/api/logs/<svc>`, `/api/update-code`,
`/api/clean-database`, `/api/symbols`, `/api/symbols/update`,
`/api/ga/{status,schedule,results,history,run,apply,rollback,log,performance,symbols}`,
`/api/bots/uptime`, `/api/active-symbols`.

**v1-only (v2 ушёл от них):**
`/api/trader-stats`, `/api/symbol-breakdown`, `/api/divergence`, `/api/slippage`.

## Перед правкой backend (`dashboard_api_v3.py`)

1. Понять — это endpoint v2-only, общий или v1-only?
2. Если v2-only — фронт v2 контракт зависит от формата response
3. Если общий — оба фронта получат изменение, проверить оба
4. Если v1-only — v2 не пострадает, безопасно
5. После правок: `systemctl restart dashboard-api && curl -s 127.0.0.1:8000/api/<endpoint>` для проверки обоих контрактов

## Cutover триггер

Когда Артём скажет «оставляем v2 как основной»:
1. `cp /var/www/dashboard/index.html /var/www/dashboard/v1.html` (бэкап старого)
2. `cp /var/www/dashboard/v2.html /var/www/dashboard/index.html`
3. Switcher на v2 поменяет href: `<a href="/v1.html">v1</a><a href="/" class="active">✨ v2</a>`
4. Удалить v1-only endpoints в `dashboard_api_v3.py` (не раньше)
5. Удалить TRADING_DASHBOARD.html из репо (или переименовать в `LEGACY_DASHBOARD_v1.html`)
