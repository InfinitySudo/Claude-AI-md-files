---
name: Real-trading snapshot endpoint
description: /api/real-snapshot bundles wallet+open+realized 1h/24h/7d for hourly reports; uses Bybit truth, not DB
type: project
originSessionId: caeefaeb-72c6-46d0-859e-af583c161299
---
## Что есть с 2026-05-06

`GET /api/real-snapshot` — единый endpoint для real-trading метрик. Используется в `scripts/hourly_supervisor.py` для секции «💰 real trading» в часовом отчёте.

Возвращает:
- `wallet` / `equity` / `upnl` из `/v5/account/wallet-balance`
- `open` — список позиций с mark-price, по-стратегийный count, total uPnL, worst-loser
- `realized.1h/24h/7d` — net + chunks + fees через `get_bybit_realized_pnl(since_ms)`
- `issues` — orphans в обе стороны (DB↔Bybit drift)

## Почему Bybit, а не DB

Per `feedback_real_trades_truth.md`: DB врёт по real PnL (orphan opens + double-count partial chunks). Headline metrics ВСЕГДА через Bybit closed-pnl, не через `realized_pnl_usd`.

## Стоимость

Каждый вызов = 3 windows × N traded symbols Bybit closed-pnl запросов. Для активного бота с 30+ символов в 7d = ~90 API calls. Bybit лимит 600/sec — некритично. Кэш 120s между вызовами на ОДИНАКОВОМ since_ms.

## How to apply

Когда надо где-то ещё (Grafana/CLI/notifier) показать «текущее состояние real-торговли» — этот endpoint, не SQL по real_trades. Для часовых snapshots — он. Для real-time дашборда — `/api/trader-stats?source=real` (там более полный set).

Если Артём попросит исторические wallet snapshots (e.g. «wallet Δ vs прошлый час») — Bybit не публикует историю балансов, нужно отдельно сохранять snapshots в БД (хук в hourly_supervisor → INSERT в новую таблицу `wallet_snapshots`).
