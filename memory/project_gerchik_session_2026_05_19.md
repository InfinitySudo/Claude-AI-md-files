---
name: gerchik-session-2026-05-19
description: Большая сессия 2026-05-19 — 9 фильтров в agent_levels + auto_flipper + BNB ручной flip; контекст рынка и какие коммиты пушнуты
metadata: 
  node_type: memory
  type: project
  originSessionId: fdfe8ecb-6a09-4f66-8869-b95289919a5d
---

День интенсивной отладки gerchik-trading-agent (sub3) — Артём заметил flip-flop торговлю, начали разбирать, кончили большим набором guards.

**Что починили (коммиты в `InfinitySudo/gerchik-trading-agent`, branch main):**

1. `d6f47c4` — opposite-side gap guard (one-way mode flip-flop)
2. `e169834` — position-aware path-to-TP guard
3. `2796fa4` — same-side averaging-into-loss guard
4. `5e2a811` — content-based dedup (закрыл hour-bucket loophole в `_make_link_id`)
5. `bae2ce5` — HTF trend guard (4H+D EMA50 strict=False) + setup_grade в DB
6. `322df7c` — dynamic RR=opposite-level TP, min 1:3
7. `84783cc` — TG карточка с RR/WR/HTF
8. `6ffb4c6` — auto_flipper (BNB manual flip + XRP triggered watcher)
9. `c2f09f6` — Tier-1: funding rate + BTC corr + volume context в reasoning

## Контекст рынка (snapshot 2026-05-19 ~10:30 MDT):
- BNBUSDT: 4H+D bias=down, цена 638-640 в боковике 580-680
- XRPUSDT: 4H+D bias=down, цена 1.36-1.38, явный downtrend после январского пика
- ETHUSDT: 4H+D bias=down
- BTCUSDT: 4H=down, D=up (mixed)
- SOLUSDT: 4H+D bias=down

## Открытые позиции AI-agent (sub3) на конец сессии:
- BNBUSDT **Short 0.08** @ 639.2, SL=653.6, TP=591.8 (RR=1:3.29) — ручной flip Long→Short
- XRPUSDT **Long 80** @ 1.3797, SL=1.3391, TP=1.461 — ждёт auto_flipper триггера на 1.3826

## Active AI pending levels (4):
- id=138 BTCUSDT Buy @ 72000.5 (RR=1:4.88, grade=medium)
- id=139 BTCUSDT Sell @ 79071.2 (RR=1:4.88, grade=medium)
- id=140 ETHUSDT Sell @ 2201.0 (RR=1:5.38, grade=strong)
- id=141 ETHUSDT Sell @ 2396.4 (RR=1:3.48, grade=strong)

## TG-карточка теперь содержит:
```
📍 AI Level placed
🔴 SYMBOL SIDE @ price
Type: ... · Conf: ...
📊 RR 1:N · TP · SL
🟩 Grade strong · est. WR 65%
📈 HTF: 4H down · D down
💭 Claude reasoning (видит volume_ratio + POC + HTF + BTC + funding)
```

## Что отложено (Tier 2/3):
- Бэктест framework — без него все дальнейшие улучшения = вера. Подождать 50-100 closed real trades.
- Расширенный pattern_detector (divergence, inside-bar, exhaustion)
- 1H EMA(20) alignment
- Market regime (ADX > 25 = trending, < 20 = range)
- Order-book imbalance (Bybit WS depth)
- ML scoring (meta_labeler уже есть, но мало данных)

## Связанные:
- [[feedback_agent_levels_guards]] — полная цепочка 9 фильтров и DB схема
- [[project_gerchik_auto_flipper]] — модуль auto_flipper
- [[project_gerchik_bot]] — main spec проекта
- [[project_bybit_3sub_architecture]] — sub1/sub2/sub3 аккаунты
