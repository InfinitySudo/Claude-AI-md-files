---
name: ga-backtester-daily-zero-bug
description: "На ПК1 GA backtester (pipeline.evaluate_strategy) сейчас выдаёт 0 trades при любых params — daily ATR=0 для всех 60k signals. Root cause: arr_d_hl всё нули. Cache stale или loader name-mismatch. Phase 1 BTC sanity (`scripts/gpu/btc_sanity_check.py`) ловит это сразу."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Симптом (был):** GA recommended (или baseline) params на ПК1 → 60k+ raw signals → 4866 после cooldown → **0 trades** (все `exits == 8 = EXIT_SKIP`).

**Root cause НАЙДЕН и ИСПРАВЛЕН 2026-05-13** (commit ca78b73 в 4BotsBybit-Trading): timezone bug в `btc_sanity_check.py:_parse_dt`. `dt.datetime.strptime(...).timestamp()` без `.replace(tzinfo=utc)` → epoch с **local-time offset** (на VPS Mountain Time = UTC-6/7). Bybit daily bars stamped at 00:00 UTC; `ts_to_idx[grid_start_ms + i*DAY_MS]` строится с local-time grid_start_ms → off by 6-7h от daily bar timestamps → **ни один daily bar не попадает в slot** → `arr_d_hl` остаётся all-zero → ATR=0 → EXIT_SKIP всем signals.

Fix mirrors original `ga_optimizer_gpu.py:parse_dt` который правильно `.replace(tzinfo=timezone.utc)`.

**Yesterday's GA работал** потому что использовал свою корректную `parse_dt`, а я вытащил скопированную «упрощённую» в sanity script. Только sanity был broken — не сам GA.

**Как поймать впредь:**
```bash
# Run on PK1 in ga_gpu venv
python btc_sanity.py
# If output shows `BTC: 0 trades, universe: 0 trades` and signals_total>1000 — broken
```

`scripts/gpu/btc_sanity_check.py` — готовый smoke-test. Принимает `--symbols-file` (default full universe), запускает все 3 стратегии, печатает {BTC, universe} статистики. Если универсальный pnl=0 — ATR broken.

**Чтобы починить:**
1. На ПК1 проверить какие daily файлы загружаются: print `_all_cache_files(cache_dir, symbol, "bybit", "D")` для BTCUSDT
2. Refresh cache через какой-нибудь scrape script если есть
3. Альтернатива — patch `_atr_for_signals` чтобы fall back на 5m ATR когда daily=0

**Связь:** pipeline.evaluate_strategy теперь возвращает 3-tuple `(pnl, ts, sym_idx)` (since 2026-05-13 c5c13a1) — sanity script это использует чтобы post-filter BTC. Не путать с pre-c5c13a1 версией.

Не блокирует tutor-боты или другие проекты. Только GA optimization halted до восстановления cache.
