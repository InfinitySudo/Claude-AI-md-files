---
name: ga-realism-overhaul-2026-05-13
description: Overhaul GA backtester (4 фазы + 2.5) сделанный в одной длинной сессии 2026-05-12/13. Sharpe annualised + costs + live constraints + BTC/ETH/SOL blacklist + per-symbol PnL breakdown. GA recommendations теперь приземлёнее.
metadata: 
  node_type: memory
  type: project
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Контекст:** Артём заметил что GA result показывает Sharpe 30-70 и +$8721 net P&L в test за 4 недели — нереалистично. Хотел перед apply исправить backtester чтобы числа соответствовали реальному miror live. Сделал 4 фазы + бонус 2.5 и Phase 1 diagnostics в одну сессию.

### Что изменено в коде (`scripts/gpu/`)

**`ga_optimizer_gpu.py`:**
- `SLIPPAGE_PCT_PER_SIDE`: 0.05 → 0.10 (Bybit realised live). `FUNDING_PCT_PER_TRADE = 0.011` (≈0.03%/day × 3h avg hold). `pnls_array -= 2*slippage + funding` в `_compute_fitness`.
- Sharpe per-trade (mean/std × √n_trades, давал 30-70) → **annualised daily** через `_annualised_daily_sharpe(pnls, ts_ms)` — bucket by UTC day, `mean(daily)/std(daily) × √252`. `SHARPE_OVERFIT_CAP` 25 → 10.
- `_split_pnls_at` / `_fold_score` / `_strategy_metrics` пропускают `ts_ms` через walk-forward, иначе fallback (per-trade × √(252/30)) даёт inflated значение.
- `main()` читает env-overrides: `GA_MAX_CONCURRENT` (100), `GA_HOURLY_DD_CAP_PCT` (10.0), `GA_AVG_HOLD_HOURS` (3.0), `GA_BLACKLIST_SPIKE_MIN` (6.0). Builds `_DATA["blacklist_sym_indexes"]` из {BTCUSDT, ETHUSDT, SOLUSDT} ∩ accepted.
- `base_params` в `evaluate()` и `_build_canonical_result()` несут все 5 tunables в pipeline.

**`pipeline.py`:**
- `_apply_live_constraints(pnls, ts, sym_idxs, max_concurrent, hourly_dd_cap_pct, avg_hold_hours)` — sequential post-filter после GPU pass: позиции открыты `avg_hold_h` часов в heap, новый signal skip если `>= max_concurrent` или текущий hour-bucket уже frozen из-за DD.
- Blacklist filter перед simulate: если `params["spike_ratio"] < blacklist_spike_min`, обнуляет `taken[sym, :]` для всех blacklist syms.
- `evaluate_strategy` возвращает **3-tuples** `(pnl, ts, sym_idx)` (был 2-tuple). + helpers `strip_sym()`, `filter_by_sym()`.

**Sanity script `btc_sanity_check.py`:**
- Load full universe, run все 3 strategies, post-filter по `sym_idx == BTCUSDT_idx`. Возвращает {btc, universe} stats. Single-symbol mode сломан (signals → EXIT_SKIP), поэтому всегда full-universe.
- **CRITICAL fix**: `_parse_dt` использовал `.timestamp()` без `tzinfo=utc` → local-time epoch → ts_to_idx miss всех Bybit daily bars (00:00 UTC) → daily ATR = 0 → 0 trades. Mirror original `ga_optimizer_gpu.parse_dt`. См. [[feedback_ga_backtester_daily_zero]].

### Dashboard UI (`index_v2.html` + `dashboard_api_v3.py`)
- **`POST /api/ga/diff`** — read-only resolver: для каждого gene-key возвращает текущее value из signal_json / trading_json / bot_settings DB. BE percentages конвертируются обратно в fractions.
- В `renderGaRecommended`: collapsible **«📋 Все параметры (current → recommended)»** с table {Scope, Param, Current, Recommended, Δ%}. Group by CONS/TREND/AGGR/GLOBAL. Цвета: серый <2%, зелёный +, оранжевый −.

### Phase 1 finding (sanity результат)

Apples-to-apples (baseline params, 3-day window, same code path):
- GA backtest universe per-strategy: 1227 trades, +346% pct sum, **+0.28% mean per trade**
- Live paper CONS only:            668 trades, +171% pct sum, **+0.26% mean per trade**

**Per-trade edge calibrates correctly** (0.28 vs 0.26, ~7% off — в пределах нормы). Backtester НЕ overestimates skill. Bottleneck — **overgenerates trades в ~1.8×** vs live. Это закрывает Phase 2 post-filter (max_concurrent=100 + hourly_dd_cap) — на следующем GA run trade count должен опуститься ближе к live.

BTC отдельно: -1% (GA-rec) или -9.4% (baseline) — слабый символ на текущих params. Phase 2.5 blacklist спайк-rule правильный.

### Env config

Чтобы изменить tunables перед GA run (на PK1 или PK2):
```powershell
$env:GA_MAX_CONCURRENT="100"
$env:GA_HOURLY_DD_CAP_PCT="10.0"
$env:GA_AVG_HOLD_HOURS="3.0"
$env:GA_BLACKLIST_SPIKE_MIN="6.0"
```
Log printed at startup: `[load] live-constraints: max_concurrent=X hourly_dd_cap=Y% avg_hold=Zh blacklist=N syms min_spike=M`.

### TODO state

1. ✅ **UI for GA tunables (DONE 2026-05-13)** — 4 entries в `SETTINGS_REGISTRY` (`ga_max_concurrent`, `ga_hourly_dd_cap`, `ga_avg_hold_hours`, `ga_blacklist_spike_min`). Edit panel «🛠 GA Realism Guards» в дашборде. New `GET /api/settings/{key}` endpoint. Wrapper script `C:\Users\tkach\ga_gpu\run_ga_with_settings.ps1` на PK1 — curl'ит VPS перед стартом GA и экспортит env. Commit `e22cb9c`.
2. ⏳ **Re-run GA on PK1 запущен 2026-05-13 ~06:00 UTC** (PID 5860), ~16 мин — Артём увидит результаты утром в дашборде. Должно: Sharpe ≤ 10, меньше trades (constraints active), BTC/ETH/SOL пропущены при spike<6.
3. ⏸ **Extra genes 31-33** для GA tuning self-constraints (max_concurrent, hourly_dd_cap, avg_hold) — большая правка `GENES`, `decode_individual`, `mutate_individual`. Отдельная сессия.
4. ⏸ klines cache (~1.5GB) только на PK1. Если хочется параллельных GA runs — scp на PK2. Low priority.

### Якоря
- [[project_pc2_homelab_active]] — PK2 GA-ready (cupy + wheels + GA modules)
- [[feedback_ga_backtester_daily_zero]] — timezone bug + history sanity-debug
- [[project_dashboard_ga_section]] — UI references
- [[project_ga_optimizer]] — original GA project spec
- [[feedback_ga_apply_full_chain]] — где GA apply пишет (signal_json/bot_settings/trading_json)
- [[feedback_ga_fitness_overfit]] — old MIN_TRADES thresholds
- [[project_backtest_findings]] — spike=6 BTC/ETH +42% (источник blacklist threshold)
