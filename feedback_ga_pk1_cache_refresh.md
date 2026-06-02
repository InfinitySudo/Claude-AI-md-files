---
name: feedback_ga_pk1_cache_refresh
description: Как обновлять kline-кеш GA-GPU на PK1 и три ловушки (dashboard_symbols.txt / хардкод-окно / zero-fill маскирует стале-кеш)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b67042b8-ce41-4a32-b089-85c0f49c7306
---

GA-GPU на PK1 (`C:/Users/tkach/ga_gpu`) читает kline-кеш `klines/binance_<SYM>_5_<start>_<end>.json` (5m, Binance, есть buy/sellVolume) + `bybit_<SYM>_D_<...>.json` (daily, ATR). **Кеш НЕ докачивается автоматически** — `ga_optimizer_gpu`/`kline_loader` только читают и мёржат по ts через glob. PK1 не имеет `src/`, поэтому префетч — на VPS, потом scp.

**Три ловушки (все 2026-05-31):**
1. `run_ga.ps1` читает символы из **`dashboard_symbols.txt`** (не symbols.txt / symbols_live.txt). Дашборд `_start_ga_on_pc1` пишет туда из `_ga_active_symbols()` (config/symbols.json). При прямом запуске ps1 этот файл может быть стале.
2. Окно: `run_ga.ps1` имеет **хардкод-дефолты `-Start 2026-02-06 -End 2026-05-06`**; ни ps1, ни `_start_ga_on_pc1` НЕ передают даты → стале-окно. Всегда передавай `-Start/-End` явно.
3. **Zero-fill маскирует устаревший кеш:** loader держит символ если заполнено >50% грид-баров; при окне до 31 мая на кеше до 6 мая последние ~3 недели = НУЛИ (мусор), но прогон «успешен». Лог это не печатает (только skipped). Косвенный признак свежести — время загрузки выросло (20s→42s).

**Процедура обновления (повторяемо):**
1. `scripts/prefetch_pk1_gap.py` (committed a7f3da9) — фетчит gap (правь START/END ms внутри) для `/tmp/symbols_live.txt` через `src.backtest.fetch_klines` в VPS `data/klines`. ~235/252 ок (6 делистед: ZEC/HFT/AIXBT/ZBCN/ZkJ и т.п. — loader их и так skip'нет).
2. В `data/klines`: `tar -czf /tmp/gap.tgz binance_*_5_<s>_<e>.json bybit_*_D_<s>_<e>.json` → scp на PK1 → `tar -xzf ../gap.tgz` в `klines/` (у Windows есть tar.exe). ⚠️ ВАЖНО: тарить ТОЛЬКО после полного завершения префетча (bg-задача), иначе уедет частичный набор — так и случилось (14 из 235).
3. Kill старый PID (`Stop-Process -Id <pid> -Force`), запусти `run_ga.ps1 -Pop -Gens -Seed -Start -End`, PID из `ga_run.current`.
4. Проверь лог: «N symbols, window …», «… accepted», время загрузки (~42s = свежий).

Связано: [[project_ga_optimizer]], [[feedback_ga_symbols_single_source]], [[feedback_ga_prewarm_418]].
