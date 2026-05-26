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

### AGGRESSIVE (REAL) — применено 2026-05-26 00:54 по моей рекомендации
- `tp_ratios: [2.5, 10.0, 15.0, 20.0, 25.0]` ← поднял TP1 до 2.5R по прогнозу +$35/мес
- `tp_distribution: [1.0, 0.0, 0.0, 0.0, 0.0]` ← закрывает всю позицию на TP1
- `be_activation_pct: 1.3` / `be_offset_pct: 0.8` ← вернул BE_act к 1.3% (BE заработает)
- `financial.tp_order_type: Limit` ← maker fees для TP (экономия ~$0.05/TP)

История прыжков 2026-05-26: 1.5R/1.3/0.9 → 3.0R/2.5/1.6 → 1.85R/1.6/1.1 → **2.5R/1.3/0.8**.
- `leverage_min: 50` / `leverage_max: 80`
- See [[project-tp-shadow-ladder]] для мониторинга что мы недобираем после 100% TP1.

**КРИТИЧЕСКИ ВАЖНО — смешанная семантика параметров (источник `src/trading_bot_bybit.py:_be_params_for + _calculate_aggressive_tp`):**
- `tp_ratios[i]` — **R-multiples of SL distance** (TP_price_pct = ratio × sl_distance_pct)
  - подтверждено UI dashboard: "AGGR TP1 (xR) range: 0.5 – 80"
  - подтверждено описанием CONS: "SL=0.6%, R=1.5 → +0.9% from entry"
- `be_activation_pct` — **процент от entry price напрямую** (НЕ R-multiple): `activation_price = entry × (1 + pct/100)`
- `be_price_offset_pct` — **процент от entry price** (НЕ R): `be_price = entry × (1 + offset/100)`
- `sl_multiplier` в strategy_parameters — **legacy, не используется** (реальный мультипликатор в `bot_settings.atr_multiplier`)

⚠️ **Trap новых AGGR настроек (2026-05-26)**: при текущем atr_multiplier=0.25 и avg SL=1.10% → TP1=3R=3.30%. BE_activation=2.5%. Цена должна пройти 2.5% чтобы BE armed, потом ещё 0.8% до TP1. **BE armed раньше TP**, нормально. НО если изменить atr_multiplier на 0.15 (SL avg=0.66%) → TP1=3R=1.98%, BE_activation=2.5%. **TP1 hit раньше BE armed → BE не работает никогда** при узком SL. Поэтому BE_activation тоже надо снижать вместе с SL.

Глобальные TP% legacy в bot_settings (НЕ используются для AGGR): `tp1_percent=1.5`, `tp2_percent=2.5`, `tp3_percent=4.0`.

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

## 13. Реальная математика на 161 real AGGR trades (since 2026-05-21)

**Источник истины — не симуляция, а наши фактические сделки.** 1R мерим по SL closes (там qty не уменьшен партиалом) → **avg 1R = $0.871** (не $0.61 как ошибочно писал раньше — то было среднее по всем закрытиям включая partial qty).

### Per-bucket факты (n=161, исключая 18 noise rows: CONSOLIDATED/ORPHAN):

| Bucket | n | freq | avg $/trade | sum $ | avg 1R | fee/trade |
|---|---:|---:|---:|---:|---:|---:|
| SL | 72 | 45% | −0.988 | −71.15 | $0.871 | $0.140 |
| BE | 58 | 36% | +0.137 | +7.93 | $0.270 (partial) | $0.107 |
| TP1 | 30 | 19% | +1.661 | +49.82 | $0.654 (partial) | $0.174 |
| **TOTAL** | **161** | — | **−0.083** | **−13.36** | — | — |

- Net per trade: **−$0.083** (наблюдаемый −$0.076 учитывая 18 noise rows + 1 FORCE)
- Total fees AGGR real: **$22.38** на 179 trades = **$0.125/trade**
- **Без fees**: gross был бы **+$8.76** (mечтательно близко к break-even)

### Break-even formula at current mix (45% SL / 36% BE / 19% TP):

```
need_TP_win × 0.19 = avg_SL_loss × 0.45 − avg_BE_win × 0.36
need_TP_win = ($0.988 × 0.45 − $0.137 × 0.36) / 0.19 = $2.08
```

При текущей частоте hits — нужен **TP1 win $2.08** (сейчас $1.66). Это эквивалентно **TP1 = 2.39R** (а не 1.5R как было). **3R — overshoot**, потому что увеличение TP в R снижает hit-rate пропорционально.

### Что значит Артёмово изменение 2026-05-26 (TP1 1.5R→3R, BE 1.3/0.9→2.5/1.6) для тех же 161 trades

Используя `peak_pnl_pct` real_trades (= max favorable % для wins, max adverse для losses):
- **Сколько достигают TP1=3R (price move ≥ 3.3% при avg SL=1.10%)**:
  - Из 30 текущих TP-bucket: **18 trades** имели peak ≥ 3R (60% from current TP-winners)
  - Из 58 BE-bucket: **2 trades** имели peak ≥ 3R (рудиментарно)
  - Из 72 SL-bucket: **0** (peak max +0.559%)
  - **Итог: 20/161 = 12.4% TP hit-rate (vs 18.6% old)**

- **BE_activation=2.5% при avg SL=1.10%**:
  - Из 58 BE-bucket: **0 trades** имели peak ≥ 2.5% (max peak BE=1.496%)
  - Из 30 TP-bucket: **12 trades** имели peak ≥ 2.5%
  - **BE armed только в ~7% сделок (vs 36% old)** — это значит почти все BE-кандидаты идут в SL по полному 1R

- **Оценка нового NET на тех же 161 trades**: ≈ **−$95** (vs OLD observed −$14).
  - 20 TP × $2.61 = +$52
  - ~6 BE wins (из 12 ex-TP с armed BE, половина retrace до BE) × $1.27 = +$7.60
  - 134 SL (72 + 56 ex-BE без защиты + 6 ex-TP не дотянувшие) × $-0.988 = $-132
  - Fees ~$22

**Вывод**: новые настройки 2026-05-26 хуже старых в 7x по убытку. **Основная причина — BE_act=2.5% слишком высокий**, BE-защита не работает. Если оставлять TP=3R, BE_act обязательно снизить до ~1.3% (offset ~0.9%) → потеряем 4 BE-bucket-trades которые сейчас выходят в +1.3..1.6%, зато не проиграем 56 BE-trades которые без защиты пойдут в SL.

### Ответ на вопрос «уменьшить SL до 15% ATR — увеличит ли TP1?»

**ДА, увеличит — но мало**, потому что TP1 в % движения = R × SL_pct. При SL=15%ATR=0.66% → TP1=3R = **1.98%** (vs 3.30% при 25%ATR). Цене нужно меньше пройти.

На real-данных peak distribution:
- peak ≥ 1.98% (= TP1=3R с узким SL): из TP-bucket 22 trades, из BE-bucket 0, из SL 0 → ~23/161 = **14.3% TP hit-rate**
- vs **12.4%** при SL=25%ATR + TP1=3R

Прирост TP-rate +2 пункта (с 12.4% до 14.3%) = **+3 trades которые станут TP**. Win добавит ≈ $3 × $2.61 × 0.6 = +$4.7. НО **больше false SL-trigger**: peak/trough в real broken proxy, нельзя точно посчитать. На paper статистике (см. § ниже) каждое снижение SL добавляет 5–8% к SL-rate.

### Ограничение анализа

`peak_pnl_pct` и `trough_pnl_pct` в `real_trades` хранят **одно и то же значение** (final extreme в направлении exit). Для wins → max favorable. Для losses → max adverse. **Нет MAE для wins** (не знаем как глубоко цена ходила против перед TP) и **нет MFE для losses** (не знаем доходила ли цена до favorable territory перед SL). Это значит точную симуляцию «что было бы при SL=15%ATR» можно делать только на:
- (a) paper trades (peak/trough там корректные, той же signals pool)
- (b) bars history per trade (требует Bybit API per-trade, медленно)

### Симуляция на 341 paper AGGR trades (proxy)

См. предыдущую версию таблицы для деталей. Краткие выводы:
- OLD (SL=25%ATR, TP1=1.5R, BE=1.3/0.9): paper gross −0.13R, лучшая из «реалистичных»
- CHANGED 2026-05-26 (TP1=3R, BE=2.5/1.6): paper gross −0.44R — подтверждает что новые настройки хуже
- Лучшие найденные: **SL=10%ATR + TP1=3R + BE=1.0/0.6** (paper gross +0.13R, ~break-even на maker fees)
- **Главный рычаг — fees, не SL ширина**. Maker-only execution превращает большинство сценариев в break-even.

### Disclaimer для будущих сессий
- Real expectancy = **факт**, paper = **proxy** (те же signals, но другие BE/TP логики применялись).
- Цифры NEW настроек = **оценка**, не наблюдение. Точно узнаем через ~50 real trades после restart.

### Прогноз на новые настройки 2026-05-26 v2 (TP=1.85R, BE=1.6/1.1) + maker fees

Модель: для каждого из 161 real trade переклассифицируем по peak в новый bucket; gross win/loss масштабируем пропорционально новым TP/BE; fees заменяем. Sanity OLD: модель даёт −$14.21 vs наблюдаемое −$13.62 ✓.

| Сценарий | TP | BE | SL | NET 162 trades | $/trade | $/мес (180 tr) |
|---|---:|---:|---:|---:|---:|---:|
| OLD (TP=1.5R, BE=1.3/0.9) + taker (baseline) | 30 | 59 | 73 | −$14 | −$0.088 | −$16 |
| **NEW v2 (TP=1.85R, BE=1.6/1.1) + TAKER** | 30 | **0** | **132** | **−$69** | −$0.43 | **−$77** |
| **NEW v2 (TP=1.85R, BE=1.6/1.1) + MAKER** | 30 | 0 | 132 | **−$56** | −$0.35 | **−$62** |
| OLD settings + просто MAKER fees | 30 | 59 | 73 | **−$1.25** | −$0.008 | **−$1.4** (~break-even) |
| TP=1.85R + СОХРАНИТЬ BE=1.3/0.9 + MAKER | 30 | 59 | 73 | **+$10** | +$0.064 | **+$12** |
| TP=2R + BE=1.3/0.8 + MAKER | 30 | 59 | 73 | **+$15** | +$0.089 | **+$16** |
| **TP=2.5R + BE=1.3/0.8 + MAKER** | 30 | 59 | 73 | **+$31** | +$0.19 | **+$35** ⭐ |

### ⚠️ КРИТИЧЕСКИ ВАЖНО про BE_activation

На наших 59 real BE trades **peak_pnl_pct max = 1.496%, avg = 0.720%**. Это значит:
- `be_activation_pct = 1.3%` (старое) → 36% trades arm BE ✓
- `be_activation_pct = 1.6%` (новое) → **0 trades arm BE** — BE мёртв
- `be_activation_pct = 2.5%` (предыдущее изменение) → **0 trades arm BE** — BE мёртв

**Любое значение be_activation_pct > 1.3% уничтожает 59 BE wins в нашем сэмпле**. Они становятся 59 × $-1 = −$59 потерь без защиты.

Артёму перед каждым подъёмом BE_act спрашивать: «а что если peak < 1.6%, что станет с этими trades?» — потому что peak в наших данных rarely > 1%.

### Прогноз и рекомендации (по приоритету)

1. **Если перейти ТОЛЬКО на maker fees, ничего больше не менять**: −$1.4/мес — практически break-even, минимальный риск.
2. **Если хочется upside**: вернуть BE_act = 1.3% (или 1.0%), поднять TP до 2.0–2.5R, перейти на maker → **+$15–35/мес**.
3. **Текущие настройки (TP=1.85R, BE=1.6/1.1)** — даже с maker fees прогноз **−$62/мес** из-за убитого BE. **Откатить BE назад до 1.3/0.9 СРОЧНО**.

## 15. Conditional-Limit (maker fees) — feasibility и риски

### Где сейчас market в коде
- **Entry**: `order_executor_v3.py:205` → `api.place_market_order()` → taker ($0.0275 на $50 notional)
- **SL**: `order_executor_v3.py:569` → `set_trading_stop(sl_order_type="Market")` → taker on trigger
- **TP**: `tp_order_type` из JSON, сейчас `Market` для AGGR. Можно `Limit` через `set_trading_stop(tpOrderType=Limit, tpLimitPrice=...)` — реализовано в `bybit_api.py:333-338`.

### Как перевести на maker:
- **TP**: добавить `tp_order_type: Limit` в `config/trading_v3_artem.json:financial` (через dashboard endpoint, без правки JSON напрямую). Это **уже работает в коде**, только включить.
- **SL**: Bybit `slOrderType=Limit` + `slLimitPrice` — поддерживается API. Code в `bybit_api.py` нужно дополнить аналогично TP (передавать `slLimitPrice`).
- **Entry**: вместо `place_market_order` использовать `place_order(orderType=Limit, price=signal_price, timeInForce=PostOnly)`. PostOnly гарантирует maker fee или отмену.

### Риски maker-mode
| Риск | Последствие | Митигация |
|---|---|---|
| **Entry limit не fill** | Пропустим сигнал | TimeInForce=`IOC`-like fallback: если за 5s не fill — market entry |
| **SL limit не fill при гэпе** | Цена пробьёт SL → loss больше 1R | Bybit `slLimitPrice` всегда чуть хуже trigger (e.g. -0.1%) → limit заведомо исполняется или fallback на market |
| **TP limit не fill при whipsaw** | Цена коснулась TP но отошла — TP не fill, trade идёт дальше | Не критично — мы и так наблюдаем avg TP factor 2.96× target (исполняется выше target при сильном движении) |
| **Slippage в худшую сторону** | TP1 maker иногда хуже maker для нас | На текущих данных TP idет в плюс по сравнению с target → maker нам выгоден |

### Ожидаемая экономия
- Текущие fees: $22.38 на 162 trades = $0.138/trade round-trip
- Maker fees: 0.020% × 2 = 0.040% notional = $0.045/trade (если notional ~$56)
- **Экономия $0.093/trade × 180/мес = $16.7/мес**
- Это **больше всего наблюдаемого убытка** при сохранении других настроек

### План реализации (PLAN MODE, как требует CLAUDE.md)
1. Включить `tp_order_type: Limit` через dashboard endpoint (1 коммит)
2. Расширить `bybit_api.set_trading_stop` чтобы передавать `slLimitPrice` (1 коммит) + изменить `order_executor_v3.py` чтобы вызывать с `sl_order_type=Limit`
3. Самый сложный шаг: заменить `place_market_order` на `place_order(Limit, PostOnly)` для entry + fallback на market через 5s timeout
4. A/B тест: 20 real trades с maker, сравнить с baseline

Реализация — отдельная задача, требует PLAN MODE подтверждения от Артёма (по правилу 4BotsBybit-Trading/CLAUDE.md).

---

## 14. Старая секция: симуляция на 341 paper AGGR trades (since 2026-05-10) — для справки

Метод: для каждого paper trade взять peak_pnl_pct (MFE %) + trough_pnl_pct (MAE %) + timing → симулировать исход при разных SL/TP/BE. **`be_activation_pct` в % от entry (НЕ R), `tp_ratios` в R-multiples**. Sanity-check: OLD reproduces ~real paper close_reason mix.

| Сценарий | TP% | BE% | SL% | gross_R | net_taker | net_maker |
|---|---:|---:|---:|---:|---:|---:|
| OLD: SL=25%ATR, TP1=1.5R, BE=1.3/0.9 | 6% | 49% | 44% | −0.13R | −0.54R | −0.28R |
| **CHANGED 2026-05-26: SL=25%ATR, TP1=3R, BE=2.5/1.6** | **1%** | **2%** | **48%** | **−0.44R** | **−0.85R** | **−0.59R** |
| SUGG: SL=15%ATR, TP1=3R, BE=2.5/1.6 (BE сломан) | 3% | 1% | 56% | −0.46R | −0.87R | −0.61R |
| SL=15%ATR, TP1=3R, **BE=1.5/0.9** (BE починен под узкий SL) | 3% | 41% | 55% | −0.15R | −0.56R | −0.30R |
| SL=15%ATR, TP1=2R, BE=1.3/0.9 | 13% | 37% | 50% | 0.00R | −0.41R | −0.15R |
| SL=15%ATR, TP1=1.5R, BE=1.3/0.9 | 24% | 29% | 47% | +0.05R | −0.36R | −0.10R |
| SL=10%ATR, TP1=3R, BE=1.0/0.6 | 13% | 37% | 50% | **+0.13R** | −0.28R | **−0.02R** |

### Прямые выводы из симуляции

1. **Новые настройки 2026-05-26 (SL=25%ATR, TP1=3R, BE_act=2.5%) — статистически хуже старых.**
   - TP1 drops с 6% до 1% (3R дистанция = 3.3% — peak ≥ 3.3% только в 4 из 341 trades)
   - BE drops с 49% до 2% (BE_activation=2.5% при avg SL=1.10% означает BE armed только когда peak ≥ 2.5%; почти все BE-кандидаты теперь идут в OTHER/timeout)
   - Без BE-защиты SL hits идут полным 1R (а не 0.5R), expectancy −0.44R vs −0.13R
   - Ожидаемый убыток: ~$177 на ту же выборку из 341 trades (vs $112 на старых)

2. **Уменьшение SL до 15%ATR с TP1=3R и БЕЗ снижения BE — НЕ помогает** (−0.46R, BE не работает т.к. TP1=1.98% < BE_act=2.5%). Чтобы это работало нужно снизить BE_activation до 1.5% / offset 0.9%.

3. **Ответ на вопрос Артёма «больше ли TP1 при 15%ATR?»**: ДА но только если TP1 остаётся 3R абсолютно. При узком SL TP1 в % движения цены тоже меньше (3R × 0.66% = 1.98% vs 3R × 1.10% = 3.30%), потому больше trades достигают: 11 vs 4 (3% vs 1%). Но это всё равно мало. Реально TP1 hit-rate сильно зависит от R-multiple на TP, а не от ширины SL.

4. **Лучшие найденные настройки**: SL=10%ATR, TP1=3R, BE=1.0/0.6 → net_maker=−$0.02 (break-even на maker fees) → +$0.13R gross expectancy. SL=15%ATR + TP1=1.5R + BE=1.3/0.9 → +$0.05R gross.

5. **Главный рычаг — fees**, не SL. Maker-only execution превращает большинство сценариев в break-even или положительные.

### Disclaimer симуляции
- Sanity: симулятор OLD даёт BE=49% против реальных paper 35% (overestimates BE). Реальный движок paper немного строже к BE-arming. Цифры — directional, не precise.
- Не учитывает: time-of-day filter, blacklist filter (которые работают только в real), partial closes (для AGGR не применимо — 100% close на TP1).
- Базируется на peak/trough как final extremes, без знания каждого touch level → консервативный для BE-hit, может недоучитывать ранние TP1 hits на whipsaw.

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
