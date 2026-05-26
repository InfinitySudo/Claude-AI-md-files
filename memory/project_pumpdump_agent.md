---
name: project-pumpdump-agent
description: "Pump&Dump AI Agent — отдельный self-tuning торговый агент под пампы/дампы, отдельный Bybit sub4. Сейчас planning phase: PLAN.md в репо ждёт approval перед Phase-1 paper кодом."
metadata: 
  node_type: memory
  type: project
  originSessionId: 39232436-cb9d-48ac-a5c3-f0d2084ba307
---

# Pump&Dump AI Agent

**Repo:** https://github.com/InfinitySudo/PumpDumpAI_Agent (private)
**Local path:** `/root/PumpDumpAI_Agent`
**Status (2026-05-26 Phase 1.5+UI):** PAPER live. **568 USDT-perp символов** через 3 WS connections (shard'инг по 400 топиков). Code 48/48 pytest, systemd `pumpdump.service`, http :8004 c CORS (8003 занят voice-tutor). Sub4 keys в `.env` (gitignored). RR floor = 5R per trade; conviction-scaler 1.0→2.5×.

**Space_Live integration (commit Space_Live `43f1587`):**
- **cockpit.html** — `PUMP&DUMP AGENT` big-panel на месте PAPER DELTA (между LIVE TRADING и AI_TRADING_AGENT). 5-секундный poll `http://127.0.0.1:8004/stats` через `refreshPumpDumpPanel()`. PNL DELTA chart `REAL_STRATS = {aggressive, pumpdump}` — paper исключён.
- **strategies.html** — 4-я карточка в `AI Agents · Sub-2 / Sub-3 / Sub-4` (🚀 Pump&Dump Agent, PAPER · sub-4).
- **Hardlearned:** cockpit.html prod (`/var/www/dashboard/cockpit.html`) держит unversioned фичи (ZEN/HIDE/orbits) — НЕ затирать через `cp source → prod` без diff. См. `[[feedback-cockpit-unversioned]]` updated 2026-05-26.

**Trade lifecycle полный:** `src/tracker.py` ведёт open positions, considers TP partials / SL / BE arming / time-stop / gap slippage, пишет в journal `trade_close` с r_realized (NET), gross/fees/fee_breakdown/funding, peak/trough_pnl_pct, tp_funnel.

**Fees (PAPER == REAL):** per-leg тарифы из config.execution + risk.{maker,taker}_rate. Maker 0.018% для entry/TP когда order_type=Limit, Taker 0.055% для SL (hardlock) и market-close. Funding 0.0001/8h accruует только если позиция держится >480min. **Защита от double-count** (как в 4Bots `feedback-real-trades-fee-semantics`): realized_pnl_usd = GROSS, fees_usd = single accumulator, net = gross - fees вычисляется ОДИН раз в `_finalize`, флаг `_finalized` блокирует повторное закрытие, r_realized derives from NET.

**100% SL:** три слоя — (1) `sl_force_market_only=true` в config; (2) `executor.set_sl_tp()` всегда вызывает `set_trading_stop(Market, MarkPrice, Full, sl_size=100)` независимо от sl_order_type; (3) `tracker.watchdog_check()` каждые 30s в REAL — если позиция открыта на Bybit но SL ордера нет → emergency `close_market`. Gap-aware fill в tracker: при flash-crash через SL fill_price = реальный тик (хуже SL), не trigger — честный PAPER.
**Variant chosen by Artem:** C — Self-tuning agent (RL-lite + journal-driven weekly tuner with walk-forward + ±15%/week governor).

## Архитектура (one-paragraph)

Bybit WS streams 1-min klines + tickers → `detector` flags volume×price spikes (≥5× volume baseline + ≥3% price move in 15min + 0.62/0.38 buy/sell imbalance + 6h cooldown) → `ai_brain` (Sonnet 4.6 veto layer, 4s timeout) confirms or rejects → `risk_manager` (порт из 4BotsBybit risk_manager_v3.py, slimmed ~150 строк) сайзит позицию с hard caps + daily DD gate → `executor` (использует 4Bots `bybit_api.py`) ставит entry/SL/TP с maker-mode флагами из parent (commit `6163afe`). Каждый closed trade → `data/journal.jsonl`; nightly tuner per-cluster re-fits 4 parameters (risk_usd, sl_pct, tp_R[0], spike_threshold) с walk-forward + min 20 trades/cluster gate.

## Capital phasing (Bybit sub4 = pumpdump)

| Phase | Capital | Gate | Goal |
|---|---|---|---|
| 0 | $0 (code-only) | unit tests ≥95% | Code complete |
| 1 | $0 (PAPER) | 50 detections, WR>35%, no crashes | Paper validation |
| 2 | $10 REAL | 30 closed trades, net ≥0, DD<30% | Real micro |
| 3 | $100 REAL | Tuner runs cleanly week-over-week | Real scale |
| 4 | TBD by Artem | — | Live scale |

Kill switches: 5% daily DD halt, 3 SL streak → 24h blacklist, WS disconnect >2min → halt new entries, Sonnet down → fail-open (no veto).

## Что НЕ повторять из 4Bots

- НЕ 27-gene GA grid search ([[project-ga-under-review]])
- НЕ tight coupling с signal_bot WS — отдельная WS-подписка
- НЕ wide SL — пампы фейдят быстро (SL = max(2×ATR_1m, 1.5% × entry))
- НЕ averaging down — kills strategy on dumps that bounce

## Что переносим из 4Bots

- Position sizing формула с fee-aware `effective_sl_distance` ([[project-trading-critical-params]] §2)
- Leverage clamp [35, 80] + min-position $10
- Maker-mode flags ([[project-trading-critical-params]] §15, commit 6163afe)
- `bybit_api.py` импортируется напрямую из `/root/4BotsBybit-Trading/src/` (single source of truth для Bybit REST)

## Monitoring

Space_Live cockpit (`/root/Space_Live/public/cockpit.html`) — новая sub-tile `PUMP_DUMP_AGENT` рядом с AI_TRADING_AGENT и AI_COPY_TRADING. Polls `http://127.0.0.1:8003/stats` (PumpDumpAI_Agent http_server, контракт в `docs/PLAN.md §8`). Сейчас graceful fallback "planning phase" — серая точка, все KPI "—", без console errors. Загорится сразу после Phase-1 deploy.

**Port :8004** (не 8003 — `:8003` уже занят voice-tutor uvicorn на этом VPS, см. journal `lsof -i :8003`). Polls обновлены в cockpit + .env + PLAN.md.

**RR≥5R + conviction scaling (Артём 2026-05-26):**
- `tp.min_total_R = 5.0` (hard floor в `RiskManager.calc_sl_tp` перед любым cluster override)
- `tp.conviction_scaling`: vol_ratio 5×→20× и |price_change| 3%→10% → linear scale 1.0→2.5×
- per cluster TP defaults: bluechip [5,8,12], mid_cap [5,10,18], meme [5,12,25], low_cap [5,10,20]
- `calc_sl_tp` returns 4-tuple (sl, tps, dist, **conviction_scale**); main.py пишет scale в journal `params_used.conviction_scale` для будущего tuner анализа

Контракт `/stats`:
```json
{"mode":"PAPER","detections_24h":12,"trades_24h":4,"wins":2,"losses":1,
 "net_pnl_usd":1.47,"recent":[{"symbol":"PEPEUSDT","side":"LONG",
 "direction":"pump","net_pnl_usd":2.41},...]}
```

## Open questions Artem'у (PLAN.md §11)

1. Sub-account #4 setup — Artem создаёт сам или нужна инструкция?
2. LLM veto cost cap — ~$1/мес, OK без лимита?
3. Cluster tuning frequency — weekly OK?
4. Universe size — top-200 default, или top-100/top-300?

Не блокеры — дефолты приемлемые.

## Memory links

- [[project-trading-critical-params]] — current 4Bots risk benchmarks
- [[project-bybit-3sub-architecture]] — sub-account layout (sub4 будет добавлен после approval)
- [[feedback-real-trades-truth]] — DB лжёт; PnL truth pull из Bybit API
- [[project-ga-under-review]] — что НЕ повторять из 4Bots GA
- [[feedback-ga-fitness-overfit]] — overfit guards для tuner (min_trades, walk-forward, governor)
