---
name: project-trading-critical-params
description: "Single source of truth — текущие торговые настройки 4BotsBybit (risk/leverage/SL формула/TP/fees), реальные R-метрики на real AGGR, формулы break-even. ОБЯЗАН читать перед любым анализом торговли."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9b7a1d0f-7f87-48b6-aa9e-1e9273fc341f
---

# Trading critical parameters — single source of truth

**Last verified:** 2026-05-26 (после сессии fee-fix + break-even анализ AGGR real)
**Source files:** `/root/4BotsBybit-Trading/config/trading_v3_artem.json`, `bot_settings` table (Postgres `trading_v3`), `src/trading_bot_bybit.py`
**Authoritative override order:** `bot_settings` (DB) > `trading_v3_artem.json` > `settings.json` defaults

> **Rule of thumb:** при любом trading-анализе ПЕРЕЧИТАЙ этот файл перед расчётом. Не гадай настройки из головы (в прошлой сессии приплёл "0.8× ATR" — был неправ, см. [[feedback-trading-analysis-protocol]]).

---

## 1. Mode / strategy routing

| Strategy | Mode | Source |
|---|---|---|
| CONSERVATIVE | PAPER | `trading_mode.per_strategy.CONSERVATIVE` |
| TREND | PAPER | `trading_mode.per_strategy.TREND` |
| AGGRESSIVE | **REAL** | `trading_mode.per_strategy.AGGRESSIVE` |

- `bot_settings.forced_strategy = CONSERVATIVE` — это **разрешённая страта для signal generation**, не override mode.
- `bot_settings.strategy_mode = AUTO` — динамическое переключение по WR/thresholds (см. dynamic_risk.strategy_thresholds).
- См. [[project-hybrid-mode]] для деталей wrapper routing'а.

## 2. Risk per trade

- `risk_aggressive_usd = 1.0` ($1 на сделку для AGGR — это **target risk**, фактический 1R = $0.61 из-за округления qty к min_order_size)
- `risk_conservative_usd = 1.0` ($1 для CONS paper)
- `risk_trend_usd = 1.0` ($1 для TREND paper)
- `bot_settings.risk_per_trade = 0.5` — % от depo для динамического sizing (если используется)
- Position sizing формула: `qty = risk_usd / SL_distance_usd`, где SL_distance — см. § 3

## 3. SL — формула ATR (ВАЖНО — это всех путало)

Файл: `src/trading_bot_bybit.py:calculate_atr` + `calculate_tp_sl`

```
ATR = avg(range of LAST 5 normal daily bars)
  где: берём 15 закрытых daily bars,
       фильтр аномалий: range >= 0.5×avg AND range <= 1.8×avg,
       из оставшихся берём последние 5.

SL_distance_USD = ATR × atr_multiplier
  где atr_multiplier = bot_settings.atr_multiplier = 0.25 (актуально на 2026-05-26)

Sanity reject: если SL > 30% от entry → сигнал отбрасывается (broken ATR на shitcoins).
```

**НЕ "0.8× ATR"**, **НЕ "10% ATR"**, **НЕ "0.25% от 5G ATR"** — это `15-day filtered daily ATR × 0.25`. Так как ATR per-symbol разный, SL distance в % от entry получается **разный per symbol**:

| Метрика на AGGR real (n=179, since 2026-05-21) | Значение |
|---|---|
| SL distance avg | 1.10% от entry |
| SL distance p10 / p50 / p90 | 0.30% / 0.94% / 2.05% |
| 1R = avg risk USD | $0.612 |

История изменений `atr_multiplier`: 0.10 → 0.20 → 0.25 (текущий). Меняется через Control Bot UI или dashboard → пишется в `bot_settings`.

## 4. TP / BE per strategy

Источник: `strategy_parameters` в JSON (правится через GA / MFE calibration / dashboard) + `bot_settings.tp1/2/3_percent` (legacy override).

### CONSERVATIVE (paper)
- `tp_ratios: [1.0, 2.0, 3.0]` (R-multiples)
- `tp_distribution: [0.34, 0.33, 0.33]` (% qty per TP)
- `be_activation_pct: 1.0` / `be_offset_pct: 0.6` (см. [[project-be-per-strategy-experiment]])
- `sl_multiplier: 0.1` (legacy field, **не используется** — реальный мультипликатор в `bot_settings.atr_multiplier`)

### TREND (paper)
- `tp_ratios: [1.0, 2.0, 3.0, 4.0, 5.0]`
- `tp_distribution: [0.2, 0.2, 0.2, 0.2, 0.2]`
- `be_activation: 0.8` / `be_offset: 0.0` (BE off)

### AGGRESSIVE (REAL)
- `tp_ratios: [1.5, 10.0, 15.0, 20.0, 25.0]` — но **TP1 100% close**, остальные не активны:
- `tp_distribution: [1.0, 0.0, 0.0, 0.0, 0.0]` ← закрывает всю позицию на TP1
- `be_activation_pct: 1.3` / `be_offset_pct: 0.9`
- `leverage_min: 50` / `leverage_max: 80`
- See [[project-tp-shadow-ladder]] для мониторинга что мы недобираем после 100% TP1.

Глобальные TP% (legacy/fallback): `tp1_percent=1.5`, `tp2_percent=2.5`, `tp3_percent=4.0`.

## 5. Fees (Bybit linear perps)

- `taker_rate = 0.055%` (0.00055) — market orders (entry, BE-stop, SL-stop)
- `maker_rate = 0.020%` (0.00020) — limit orders (TP limit, новые limit-entries)
- `order_type = market` для entry (см. order_execution)
- `tp_order_type = Limit` (TP исполняется как maker)
- **Round-trip**: market entry + market SL = ~0.11% от notional
- **Round-trip mixed** (market entry + limit TP): ~0.075%

**Реальные данные AGGR real (n=179):**
- Avg fee per trade: **$0.125 = 20% of 1R = 41% of 1R round-trip**
- Это **ключевое узкое место** — fees съедают почти полтрети 1R.
- См. [[project-fees-accounting]], [[feedback-real-trades-fee-semantics]].

## 6. Leverage

- `bot_settings.leverage = 80` (default для AGGR — макс на Bybit для большинства perps)
- `financial.leverage = 80`
- `order_execution.leverage = 5` (legacy field в JSON, **не используется** — реальный в bot_settings + per-strategy `leverage_min/max`)

## 7. Trading hours

- `trading_schedule.enabled: True`, timezone UTC
- US summer (до 2026-11-01): **13:30–20:00 UTC** (6.5h)
- US winter (после 2026-11-02): 14:30–21:00 UTC
- `weekend_trading: False`
- Holidays: 10 дат в 2026 (включая 2026-05-25, 2026-07-03, 2026-12-25)
- `bot_settings.real_blocked_hours_utc = ''` (пусто — нет блока часов для real)

## 8. Risk caps & guards

| Cap | Value | Source |
|---|---|---|
| Daily max drawdown | 35.0% | `bot_settings.daily_max_drawdown_pct` |
| Weekly max drawdown | 25.0% | `bot_settings.weekly_max_drawdown_pct` |
| Total max drawdown | 30.0% | `bot_settings.total_max_drawdown_pct` |
| Max concurrent positions | 100 | `bot_settings.max_positions` |
| Max open real | 100 | `bot_settings.max_open_real` |
| Max open paper | 200 | `bot_settings.max_open_paper` |
| Per-strategy daily loss cap | 0 (off) | `bot_settings.per_strategy_daily_loss_cap_*` |

Anti-fade: **disabled** (`anti_fade_enabled=False`). Auto-blacklist: 1 day, releases at WR≥50% + 5 trades + ≥$0.5 net.

Risk officer: enabled, manual mode (`risk_officer_active_pause=false`, `risk_officer_use_llm_on_caution=False`). Last pause: 2026-05-18T23:00:21.

Все risk-гарды — **только для REAL**, paper без блоков (см. [[feedback-dd-guard-paper-skip]]).

## 9. Session baseline / wallet

- `session_start_wallet_usd = $99.86` (Артём)
- `system_baseline_v2_at = 2026-05-08`, baseline wallet $189.6
- `hybrid_baseline_at = 2026-05-18 23:14:12 UTC` — baseline для cumulative-PnL графика (см. dashboard equity SQL)
- `stats_baseline_at = 2026-05-10 05:42:10 UTC`
- `transferred_out_manual_usd = $150` (вручную выведено)

См. [[feedback-session-baseline-transfers]] про fix sub-account transfer = DD guard.

## 10. Реальные R-метрики AGGR real (since 2026-05-21, n=179)

| Bucket | n | net $ | avg $ | avg R |
|---|---|---|---|---|
| SL | 72 | −71.15 | −0.988 | **−0.481R** |
| BE | 58 | +7.93 | +0.137 | **+0.496R** |
| TP1 | 30 | +49.82 | +1.661 | **+4.079R** |
| FORCE | 1 | −0.22 | −0.223 | −0.231R |
| CONSOLIDATED+ORPHAN | 18 | 0 | 0 | 0 |
| **TOTAL** | **179** | **−13.62** | — | — |

- WR money-based: **49.7%** (89/179)
- PF: **0.82** (gross_win $62 / gross_loss $76)
- Mix без шума: TP1=19%, BE=36%, SL=45%
- **avg_R_loss на SL = 0.48R, не 1R** — BE+partial защита работает; настоящий R-multiple теряемый на SL значительно меньше 1.
- avg_R на TP1 = 4.08R — потому что TP1 ставится в **% от цены** (tp1_percent=1.5%) при SL в **% от цены** (avg 1.10%), и при широком ATR ratio высокий.

## 11. Break-even формулы (КРИТИЧЕСКИ ВАЖНО — использовать ЭТИ)

Используем формулу с реальным `R_loss` (не 1R) и round-trip fee в R:

```
R_win_min = [(1 - WR) × R_loss + fee_round_trip] / WR
```

### С реальным R_loss = 0.48R (AGGR сейчас, BE/partial защита):

| WR | fee_rt = 0.41R (taker) | fee_rt = 0.15R (maker-only) |
|---|---|---|
| 40% | 1.74R | 1.10R |
| 45% | 1.50R | 0.92R |
| **50%** | **1.30R** | **0.78R** |
| 55% | 1.14R | 0.67R |
| 60% | 1.00R | 0.58R |

### При R_loss = 1R (без BE-защиты, наивно):

| WR | fee_rt = 0.41R |
|---|---|
| 50% | 1.82R |
| 55% | 1.56R |
| 60% | 1.35R |

### Текущее состояние AGGR
- WR = 49.7%, fee_rt = 0.41R, R_loss = 0.48R → **R_win_min ≈ 1.32R**
- Observed avg R_win across BE+TP1 = (58·0.496 + 30·4.079) / 88 = **+1.72R**
- Считаем без BE как winning? Тогда avg R_win pure (TP1 only) = 4.08R на 30 трейдов из 179 = **expectancy positive если бы не было BE-неттинга**.
- **Проблема не в RR**, а в комбинации: 36% сделок уходят в BE (≈0 PnL), 45% в SL (−0.48R), только 19% в TP1 (+4R). Сумма + fees = −$13.62.

### Что реально уменьшит убыток
1. **Maker-only execution** (TP уже maker, перевести SL+entry на limit/conditional-limit) → fee_rt с 0.41R → ~0.15R → break-even WR падает до ~45%
2. **Symbol blacklist** SL-магнитов (BTCUSDT/HYPEUSDT/INJUSDT/AVAXUSDT/SOLUSDT/TAOUSDT/TONUSDT — 50–100% SL) → WR должен подняться к ~55%+
3. **Поднять `atr_multiplier`** 0.25 → 0.30–0.35 (SL дальше от noise) → меньше BE-чёса, MFE чаще достигает TP. Trade-off: R_loss растёт.
4. **Closer TP** (1.0R вместо 1.5%) → больше TP-fills, но меньше R per win. Считать через MFE distribution.

**Что НЕ работает**:
- Увеличить risk-per-trade или leverage → fees scale линейно с notional, fee/R ratio тот же
- Поднять TP1 до 2.5R+ → MFE p95 paper = 1.84%, недостижимо в >90% сделок

## 12. Related memories (читать вместе)

- [[project-fees-accounting]] — fee persistence, backfill script
- [[feedback-real-trades-fee-semantics]] — real net vs paper gross, double-count traps
- [[project-real-trades-baseline]] — критерии активации ML/Risk Officer на real
- [[project-hybrid-mode]] — per-strategy paper/real routing
- [[project-tp-shadow-ladder]] — мониторинг недополученного PnL после 100% TP1
- [[project-be-per-strategy-experiment]] — A/B BE параметров
- [[project-mfe-calibration]] — TP-тюнинг по фактическому MFE (не GA)
- [[feedback-trading-analysis-protocol]] — ВСЕГДА читать этот файл перед анализом
- [[project-real-global-guard-limitation]] — multi-strategy real ограничение
- [[feedback-dd-guard-paper-skip]] — risk-гарды только для real
- [[feedback-session-baseline-transfers]] — sub-account transfer = DD trigger
