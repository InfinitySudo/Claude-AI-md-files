---
name: project-agent-levels-2026-05-18
description: "AI Agent Levels system — Bybit pending-orders as visual chart lines, full SL/TP/fill-handler pipeline + Telegram bot, deployed 2026-05-18"
metadata: 
  node_type: memory
  type: project
  originSessionId: 49ea4545-bbbc-4b86-b277-32955052d57f
---

# AI Agent Levels (Bybit pending-orders)

Standalone система на sub3 wallet: AI Agent детектирует support/resistance,
ставит Limit-ордера с атомарным SL/TP на Bybit → каждый ордер виден как
горизонтальная линия на чарте. При fill — позиция открывается автоматически
со SL/TP уже attached.

## Архитектура (12 слоёв)

1. **DB schema** — `agent_levels` + `agent_level_events` (PG, trading_bot_v3)
2. **Bybit wrapper** — place/cancel/sync через `BybitREST.place_limit_entry`
   с `stopLoss`/`takeProfit` атомарно
3. **Engine integration** — `signal_engine.refresh_levels` → `_sync_agent_levels`
   → `agent_levels.place_level`
4. **Manual-aware boost** — `find_nearby_manual_level` в evaluate(),
   синтезирует Level из manual если AI ничего не нашёл в 0.5%
5. **Sync worker** — `agent_levels.sync_with_bybit` в `loop_once()`:
   - AI orders → status check
   - Manual orders (orderLinkId без AI_ префикса) → INSERT source='manual_artem'
   - Disappeared AI orders → /v5/order/history → filled vs cancelled
6. **Telegram bot** — `@AI_TradingAgentBot` (token 8858849403:..., chat_id 504609639)
   с inline-buttons Why/Cancel, /start auto-bootstrap chat_id в bot_settings
7. **TTL expiry** — 24h на AI levels, через `expire_stale_levels`
8. **Dashboard UI** — `/var/www/dashboard/agent-levels.html` + `/api/agent-levels`
   с filters (symbol/source/status), reasoning expand, 30s auto-refresh
9. **Statistics** — через `agent_level_events` JSONB (db_inserted, bybit_placed,
   filled, cancelled, cancelled_external)
10. **Safety guards** — max 3 AI levels per symbol (было 5), instrument-info
    кэш (min_qty/qty_step/min_notional), idempotent retry, throttle 0.5s
11. **Deploy** — sub3 wallet, gerchik-agent systemd unit, agent-levels-tg-bot.service
12. **Memory + commits** — это файл + GitHub `InfinitySudo/gerchik-trading-agent`

## Параметры (после калибровки Артёма)

| Константа | Значение | Файл | Логика |
|---|---|---|---|
| `MARKER_QTY_USD` | **50.0** | agent_levels.py:60 | $50 notional per level (Артём 2026-05-18: было $5 — слишком мало) |
| `SL_ATR_MULT` | **0.7** | agent_levels.py:402 | SL = price ± 0.7×ATR_14d (было 1.5 — на XRP 5.2% слишком широко) |
| `RR_RATIO` | **2.0** | agent_levels.py:403 | RR 1:2 (Артём оставил конвенциональным) |
| ATR period | **14d** | signal_engine.py:69 | `atr_from_klines(klines_d, n=14)` для agent_levels; copy-trader продолжает на n=5 |
| TTL | 24h | LEVEL_DEFAULT_TTL_HOURS | TTL expiry для AI levels |
| Per-symbol cap | 3 | place_level + _sync_agent_levels | Top-3 ближайших к live price |

При $50 × 14 уровней = **$700–$850 total notional**, margin @35x ≈ **$20–$25**
(35% wallet при $60 баланс).

## SL/TP формула

```python
sl_dist = SL_ATR_MULT * atr_14d  # 0.7 × ATR_14d
tp_dist = RR_RATIO * sl_dist     # 2 × sl_dist
SL = level_price ∓ sl_dist
TP = level_price ± tp_dist
```

Снапшот SL дистанций (2026-05-18 после калибровки):
- BTC ~1.7–1.9%, BNB ~2.2–2.4%, ETH ~2.2–2.8%, SOL ~2.9–3.1%, XRP ~3.0%

## link_id schema

`_make_link_id` использует **hour-bucket** (YYYYMMDDHH) в hash input:
`AI_<SYM>_<TYP>_<8hex>` где hex = sha256(symbol+type+price+hour).

Почему hour-bucket: Bybit держит orderLinkId в retention 1-2ч после cancel,
поэтому re-place в том же часе падал с `retCode=110072 OrderLinkedID is
duplicate`. Day-bucket был слишком грубо (re-place в течение дня тоже падал).

## Реальный fill 2026-05-18 (первый)

XRP **1.3797 Buy** filled автоматически:
- Position: size=7.4 (объединились 2 fill'a по 3.7), avg=1.3797, leverage=35x
- SL=1.3077, TP=1.5239 — атомарно прикрепились к позиции
- Fill-handler сработал: `[LEVEL_FILLED]` в журнал + `📨 TG fill-notify sent`
- DB: status='filled', fill_data={avg_price, cum_qty, bybit_status: 'Filled'}

## Lessons learned

1. **Module-level import** для TG send функций — `lazy from .telegram_levels_bot
   import` failed silently. Перенесли в top + alias `_send_level_filled` с
   try/except, добавили явное логирование success/skip/fail. См.
   [[feedback-emails-agent-handle-button]] для аналогии lazy-import pitfall.

2. **OAuth reuse** — `generate_reasoning` теперь читает
   `/root/.claude/.credentials.json` (тот же что у `@DexClaudCodAIBot`),
   `auth_token + anthropic-beta=oauth-2025-04-20`. Никакого `ANTHROPIC_API_KEY`
   не нужно. См. [[project-claude-telegram-bot]].

3. **Marker-orders vs real-orders** — изначально были задуманы как cosmetic
   markers ($5 notional), но Bybit при fill открывает РЕАЛЬНУЮ позицию.
   Без SL/TP atomic attach = leverage 35x голая позиция → ликвидация при
   −2.8%. Урок: pending orders с SL/TP с самого старта, не "пока marker'ы".

4. **ATR период** — 5d искажается 1-2 трендовыми днями (+8% свеча задирает
   среднее), 14d стабильнее. Не трогать copy-trader (он на 5d).

5. **Day-bucket → hour-bucket** для retry-friendly link_id. Bybit retention
   ID 1-2ч; нужно accept что идемпотентность ограничена этим окном.

6. **Per-symbol cap** — max 3 ближайших уровней, не 5+. Иначе далёкие
   ордера блокируют margin без шансов fill в обозримом будущем.

## Files / endpoints

- `/root/gerchik-trading-agent/src/agent_levels.py` — main module
- `/root/gerchik-trading-agent/src/signal_engine.py` — `_sync_agent_levels`, `find_nearby_manual_level`
- `/root/gerchik-trading-agent/src/telegram_levels_bot.py` — `@AI_TradingAgentBot` listener + senders
- `/var/www/dashboard/agent-levels.html` — UI table
- `/api/agent-levels` — JSON endpoint (filters: symbol/source/status, limit)
- `/etc/systemd/system/agent-levels-tg-bot.service` — TG listener systemd unit
- DB tables: `agent_levels`, `agent_level_events`, `bot_settings.tg_chat_id_ai_levels`

## TG bot details

- Bot: `@AI_TradingAgentBot` (id 8858849403)
- Token: `TG_BOT_TOKEN_AI_LEVELS` env var
- Chat: 504609639 (Артём)
- Senders: `send_level_notification` (placed), `send_level_filled` (filled)
- Callbacks: `why:<id>` (show reasoning), `cancel:<id>` (cancel level)
- /start auto-bootstraps chat_id into `bot_settings.tg_chat_id_ai_levels`

## Future tweaks (не сделано)

- `SL_ATR_MULT` и `RR_RATIO` вынести в `bot_settings` для тюнинга через dashboard
- Per-symbol notional override (BTC = $20, XRP = $80 etc.)
- Statistics learning loop — weekly Claude-review лучших/худших уровней
- Manual order cancel detection через `sync_with_bybit` — уже работает,
  тестить когда Артём поставит/уберёт свой уровень руками
