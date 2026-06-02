---
name: feedback_ga_binance_vs_bybit
description: GA на Binance-данных давала ФАНТАСТИКУ (win 76%); на правильных Bybit-данных edge почти нулевой (win 24%) — всегда тренить GA на Bybit
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b67042b8-ce41-4a32-b089-85c0f49c7306
---

**2026-05-31, доказано на 600 реальных сделках.** Live signalbot стримит **Bybit** 5m klines (turnover) + publicTrade. GPU-GA исторически читала **Binance** klines → spike_ratio (current/avg turnover) расходился с live в ~5×. Validation: 43 реальных сигнала прогнаны через движок — на Binance spike совпал 8/43, direction 26/43. На Bybit — **spike 600/600 (100%)**, live avg 12.86 == engine 12.86. Вход доказан только на Bybit.

**Что показал GA на правильных Bybit-данных (окно 03-01..05-31, 248 символов, pop40/gen60):**
- fitness **−14.95** (на Binance был +10.45), overfit чистый.
- TEST/OOS combined: tr=927 pnl=+392% win=**24.4%** sharpe=12 dd=27.4. Binance-фейк давал tr=7054 pnl=+15850% win=76.2% — **фантастика на чужом источнике объёмов**.
- По стратегиям (test): CONS pnl=−8 win17% (УБЫТОК даже у лучшего генома); TREND +316 win27%; AGGR +84 win28%. Все на 309 сделках — мало.
- Рекомендованные params: spike6.69 bs1.5 vol485k atr0.05 cd9 aggr_tp1.30% (живые: spike2.0 bs1.5 vol300k atr0.15 cd24 aggr_tp0.85%).

**Вывод (честный): edge на реальных данных крошечный, на грани шума.** Win 24% backtest ≈ живому 34%; +392%/2мес ДО costs, после ÷2 на slippage (реальный TP1 вдвое реже backtest: факт TP1=99 vs движок 207) и win 24% — около нуля/в минус. **НЕ применять GA-параметры в боевое** — выигрыш в пределах погрешности, риск реальный. Единственное с основанием: spike 2.0→~6 (живой пускает явный шум) — обкатать на paper-CONS, не трогая real. DD-гард, держащий счёт, ПРАВ — на чопе март-май агрессия не окупается.

**Инфра:** `GA_KLINE_SOURCE` env в kline_loader (default binance, на PK1 wrapper ставит bybit); `pk1_fetch_bybit.py` качает Bybit напрямую на PK1 (туннель Tailscale ~9КБ/с — 162МБ не перекинуть, PK1 сам тянет с api.bybit.com через WMI Win32_Process.Create, иначе Start-Process+redirect через ssh молча убивает python). Bybit REST kline БЕЗ taker buy/sell → bs% идёт по эвристике open/close 0.6/0.4, ровно как live fallback когда trade-bucket пуст. Связано: [[feedback_ga_pk1_cache_refresh]], [[project_ga_optimizer]], [[feedback_trading_analysis_protocol]].
