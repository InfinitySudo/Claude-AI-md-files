---
name: GA GPU миграция — DONE 2026-05-08 (canonical schema + dashboard wired)
description: GPU-port завершён 2026-05-08; canonical schema с train/test buckets; dashboard /api/ga/run target=pc1 + WMI detach + per-PID логи; first apply rank #1 cons+trend
type: project
originSessionId: b0493378-8df7-4334-bf78-c554bd77a27c
---
**Status 2026-05-08:** Migration ЗАВЕРШЕНА. См. также:
- `project_baseline_v2_2026-05-08` — какие commits вошли в rebuild
- `feedback_pc1_ssh_quirks` — WMI/per-PID-logs gotchas, без них background python падает молча
- `project_meta_labeler_v1` — отдельный ML pipeline на той же ПК1-инфре


**Цель:** ga_optimizer.py 31ч CPU → ~30 мин GPU, освободить VPS, ускорить итерации тюнинга стратегий.

**Стек на ПК1 (`C:\Users\tkach\ga_gpu\`):**
- Python 3.11.9 (Program Files), venv в `C:\Users\tkach\ga_gpu\venv\`
- numpy 2.4.4, pandas 3.0.2, deap 1.4.4
- **CuPy 14.0.1** (cupy-cuda12x) — этот работает, Numba CUDA на Windows морочил
- nvidia-cuda-runtime-cu12, cuda-bindings 12.9.6

**Файлы (на VPS `/root/4BotsBybit-Trading/scripts/gpu/`, scp на ПК1):**
- `simulate_trade_kernel.py` — RawKernel CUDA C, 1 trade = 1 GPU thread; `simulate_batch_gpu()` API
- `backtest_cpu.py` — standalone copy of `simulate_trade` + `STRATEGY_SPECS` для валидации
- `validate_simulate_trade.py` — 200 random trades, CPU vs GPU max_diff 9e-6 ✅
- `bench_simulate_trade.py` / `bench_scale.py` — perf бенчмарки

**Performance (RTX 3090):**
- 10k trades: 0.010s (1M trades/sec)
- 1.5M trades (~полная GA): 2.69s
- CPU baseline: 13k trades/sec на 4 ядрах VPS
- **simulate_trade speedup ~50-70x**

**Архитектура kernel:**
- Входы: entries[N], is_long[N], atr_dist[N], bars_off[N], bars_len[N], klines_flat[M,4], spec_pack[13]
- Выход: pnl_pct[N], exit_type[N]
- spec_pack: [tp_ratios×5, tp_close×5, n_tps, be_activation_pct, be_price_offset]
- max_bars=286 default
- TPs ladder с per-bar ordering heuristic (close>open → TPs first)
- BE-activation flips current_sl

**Что ещё надо (TODO):**
1. ✅ check_signal на GPU — `signal_kernel.py`, validated 328=328 exact
2. ✅ calculate_atr — port в `pipeline._atr_for_signals` CPU loop (быстро на 30k signals)
3. ✅ End-to-end pipeline — `pipeline.evaluate_strategy()`, validated 99% match (1 float32 edge case на 106 trades, PnL на совпавших exact)
4. ❌ Data loader: чтение cache `data/klines/binance_<SYM>_5_<start>_<end>.json` → 3D numpy arrays (или re-fetch с Binance API на ПК1, ~10-15 мин)
5. ❌ ga_optimizer_gpu.py — DEAP loop, walk-forward fitness aggregation, evaluate() зовёт pipeline
6. ❌ Smoke тест 5-10 symbols real data — флёш формат-quirks (negative sellVolume в cache из-за букирующегося _kline_from_binance_row `sellVolume = quote_vol - taker_buy_quote(base)` — известный prod-bug, GPU должен matchить CPU exactly)
7. ❌ Полный GA run 276 symbols на ПК1, target ETA ~30 мин

**КРИТИЧНО — НЕ ТРОГАТЬ:**
- Текущий GA на VPS работает (`ga-optimizer-1778095525.service`, gen 23/30, ETA утром 8 мая)
- НЕ изменять `src/backtest.py`, `scripts/ga_optimizer.py` пока тот процесс жив
- Все правки идут в `scripts/gpu/` папку — изолированно

**Quirks, на которые нарвался:**
- Numba CUDA на Windows: cuda-python 13.x ломает Numba binding (deprecated `from cuda import cuda`); даже с downgrade до 12.x — `cuda.is_available() == False`. CuPy решает.
- При CuPy: `UserWarning: CUDA path could not be detected. Set CUDA_PATH` — игнорить, всё работает потому что cupy ships свой runtime.
- Float32 хватает: max diff 9e-6 на 200 random trades.
- Python list → np.array marshalling доминирует на малых N — для 30k trades GPU был 0.4x. Решение: пре-аллокация numpy 3D arrays с самого начала, без Python list intermediate.

**Roadmap дальше:**
- ✅ Signal detection + pipeline validated 2026-05-07 ~22:15 MDT
- (Завтра утро) data loader → GA orchestrator → smoke test → full run
- (После validation) добавить flag в ga_optimizer на VSP чтобы триггерить ПК1 endpoint

**Файлы (VPS `/root/4BotsBybit-Trading/scripts/gpu/`, синхронизированы в `C:\Users\tkach\ga_gpu\` на ПК1):**
- `simulate_trade_kernel.py` — RawKernel для simulate_trade
- `signal_kernel.py` — RawKernel для check_signal (1 thread per (sym, bar))
- `pipeline.py` — orchestrator: detect → cooldown → ATR → simulate
- `backtest_cpu.py` — standalone CPU reference (simulate_trade, check_signal, calculate_trend, bs_ratio_from_klines, STRATEGY_SPECS)
- `validate_simulate_trade.py` / `validate_signal.py` / `validate_pipeline.py` — синтетика, все green
- `bench_simulate_trade.py` / `bench_scale.py` — perf-тесты
- `cuda_check.py` / `cupy_check.py` — sanity GPU detection
