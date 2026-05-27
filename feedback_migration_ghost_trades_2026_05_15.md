---
name: migration-ghost-trades-2026-05-15
description: 10 main TradingBot trades 2026-05-15 живут на старом UID 539929753 (теперь sub3 AI-agent) — Bybit sub1 их не видит. Объясняет $8 от DB-vs-Bybit gap.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

## Что случилось

**2026-05-15** — день миграции на 3-sub архитектуру:
- До ~14:00 UTC: main TradingBot работал на старом UID **539929753** (общий с AI-agent)
- После ~14:00 UTC: main TradingBot → новый sub1 UID **563399107**, UID 539929753 перепрофилирован как sub3 AI-agent

Main TradingBot сделал **10 trade'ов в течение этого дня** (15:20 - 23:35 UTC) на **старом UID**. Они корректно записаны в DB `real_trades` через `BYBIT_API_KEY` (старый key). После миграции API key переключился, но **те 10 trade'ов остались на старом UID** = текущий sub3 wallet.

## Список ghost-trades (для справки)

| Symbol | Closed | pnl | bybit_order_id |
|---|---|---|---|
| ZROUSDT | 2026-05-15 16:21 | -$1.04 | 57099e08-a5b4 |
| DASHUSDT | 17:54 | -$1.04 | cecf5880-4275 |
| EIGENUSDT | 17:55 | -$1.07 | 10c35904-e638 |
| KITEUSDT | 17:43 | -$1.01 | 6a8bc7b6-f8fe |
| JELLYJELLYUSDT | 19:27 | -$1.11 | 2073da70-af5f |
| LYNUSDT | 19:44 | -$0.27 | f53524cc-8fbd |
| LITUSDT | 23:34 | -$0.44 | d6930601-092a |
| EDGEUSDT | 21:46 | -$1.11 | bcc1b1f9-f012 |
| ETHFIUSDT | 23:34 | -$0.47 | 04a2b843-16d2 |
| 1000LUNCUSDT | 23:34 | -$0.46 | 7f59a70a-20a5 |
| **Total** | | **-$8.01** | |

Все имеют strategy='CONSERVATIVE', mode='REAL', живут в `real_trades`. Order_id'ы матчатся с Bybit sub3 closed-pnl за тот же window.

## Симптомы

- **Dashboard "Bybit cross-check для CONS/TREND"** — занижает на ~$8, потому что использует `BYBIT_API_KEY` (sub1) → не видит pre-migration trades
- **Grafana "Total PnL real"** — точно DB, эти trades включены (нет gap)
- **Stream B (AI-agent sub3)** — **inflated** на эти $8.01 в losses (видит ghost-trades как-будто свои)

## Что делать

- **Не bug, не lost money** — trades корректно записаны в DB. Это переходное состояние одного дня.
- **Через ~30 дней** ghost trades выпадут из стандартного Bybit closed-pnl 30d-window (мы сейчас 2026-05-17 → ghosts от 05-15 выпадут после 06-15).
- Если нужна **точная атрибуция** прямо сейчас: исключать ghost trades из Stream B через `bybit_order_id` match (есть в `real_trades.bybit_order_id` — `57099e08, cecf5880, ...`).

## Bybit запрос для проверки

```python
# Bybit sub3 (uses BYBIT_AI_AGENT_API_KEY) closed-pnl для 2026-05-15 14:00-23:59 UTC
# должен вернуть ровно 10 fills совпадающих с DB ghost list
GET /v5/position/closed-pnl?category=linear&symbol=ZROUSDT&startTime=...&endTime=...
```

## Связано

- [[project-bybit-3sub-architecture]] — UIDs для всех 3 sub-аккаунтов
- [[feedback-real-trades-truth]] — другие источники DB-vs-Bybit drift (partial chunks, orphans)
- [[feedback-streams-a-b-c-terminology]] — Stream B sourcing
- [[feedback-bybit-env-symlink]] — env symlink trap
