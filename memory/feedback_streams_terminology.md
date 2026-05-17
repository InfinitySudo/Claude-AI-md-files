---
name: streams-a-b-c-terminology
description: "Stream A = Gerchik copy (sub2), Stream B = AI-agent (sub3), Stream C = переименован в Main TradingBot (sub1). Не путать!"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

На дашборде `index_v2.html` (compare pane) три карточки:

| Label | Sub | Bot codebase | DB table | Где смотреть данные |
|---|---|---|---|---|
| 📥 **Stream A — Gerchik copy** | sub2 (UID 563470305) | `/root/gerchik-trading-agent/src/copy_executor.py` (signals_bot via TG @GTE_AI_TradingBot) | `gerchik_copy_trades` | DB |
| 🤖 **Stream B — AI-agent** | sub3 (UID 539929753) | `/root/gerchik-trading-agent/src/signal_engine.py` (Gerchik-style auto agent) | `gerchik_trades` | **Bybit closed-pnl напрямую** (BYBIT_AI_AGENT_API_KEY), since 2026-05-15 migration |
| 💰 **Main TradingBot (sub1)** | sub1 (UID 563399107) | `/root/4BotsBybit-Trading/src/main_bot_v3.py` (CONS/TREND/AGGR multi-strategy) | `real_trades` | DB |

## Why Stream B читается с Bybit, а не DB

`gerchik_trades` имел pyramid-bug до 2026-05-16: записывал каждое add-on entry как отдельную row → PnL inflated 3.4×. Pyramid fix (commit `dbea126`) исправлен, но historic rows не чищены. Stream B endpoint `/api/v2/gerchik/comparison` отдельно вызывает Bybit `/v5/position/closed-pnl` для sub3 и собирает aggregate truth.

После того как pyramid-fix отработает на нескольких десятках live trade'ов, можно будет switch Stream B обратно на DB-aggregation (один row на позицию = правильный qty/entry_price/avg). Но до тех пор — Bybit truth.

## Why "our agent" → "Main TradingBot"

Стрим C исторически назывался "our agent", что путало: AI-agent (sub3 gerchik-trading-agent) — это **другая** программа. Sub1 main TradingBot — multi-strategy bot CONS/TREND/AGGR, не AI-agent. Переименование сделано в `dashboard_api_v3.py` (stream_c.label) и в HTML (`compare-c-kpis` header).

## Endpoint

`GET /api/v2/gerchik/comparison?bucket=1h|6h|1d`

Response: `stream_a, stream_b, stream_c` blocks + `equity.a/b/c` arrays для chart.

## Связано

- [[project-bybit-3sub-architecture]] — UIDs, env vars, IP whitelist
- [[project-pyramid-fix-gerchik-trading-agent]] — почему gerchik_trades врёт исторически
- [[feedback-real-trades-truth]] — Bybit-as-truth pattern
