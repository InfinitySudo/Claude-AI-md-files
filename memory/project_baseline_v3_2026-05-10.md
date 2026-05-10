---
name: Baseline V3 — 2026-05-10 05:28:55 UTC
description: Чистая точка старта новой статистики после волны фиксов 2026-05-09; всё что до неё — мусор, для решений не использовать
type: project
originSessionId: 93067773-cafa-4ab3-b8c6-cf84bdc85eda
---
## Точка отсчёта

**`2026-05-10 05:42:10 UTC`** — Артём ручно объявил новый baseline + **полная очистка БД** после серии фиксов 2026-05-09 (full wipe вместо мягкого reset что был в 05:28:55).

Wallet на момент baseline: **$189.60** (зафиксирован в `bot_settings.session_start_wallet_usd` — Total DD baseline reset).

## Что сделано при full wipe (2026-05-10 05:42:10 UTC)

1. **Backup снапшоты** в таблицы (НЕ удалять — audit):
   - `simulated_trades_archive_20260510_baseline_v3_clean` — 1826 строк
   - `real_trades_archive_20260510_baseline_v3_clean` — 78 строк
   - `signals_queue_archive_20260510_baseline_v3_clean` — 3646 строк
   - `accepted_signals_archive_20260510_baseline_v3_clean` — 3270 строк
   - `strategy_statistics_archive_20260510_baseline_v3_clean` — 1110 строк
   - `simulated_trades_baseline_v3_snapshot` — старый snapshot от 05:28 (1825 строк, оставлен для исторической точки сравнения)
2. **TRUNCATE с RESTART IDENTITY** торговых таблиц:
   - `simulated_trades` → 0
   - `real_trades` → 0
   - `signals_queue` → 0
   - `accepted_signals` → 0
   - `strategy_statistics` → 0
   - sequences сброшены к 1
3. **`bot_settings.stats_baseline_at`** = `2026-05-10 05:42:10 UTC`.
4. **`bot_settings.session_start_wallet_usd`** = $189.60.
5. На Bybit: 0 реальных позиций. Всё чисто.

## Что считать мусором (pre-baseline)

Всё что в `simulated_trades` с `entry_time < 2026-05-10 05:28:55 UTC`. Причины из сегодняшнего разбора:

- WS interim-bar bug → spike-расчёт ломан, сигналы шли в случайные моменты на границах баров (НЕ репрезентативная выборка).
- Hard cap двойной счёт → TREND/AGGR размер позиций $1.43 вместо $50 (PnL копеечный, абсолютные метрики бессмысленны).
- WS keepalive до коммита `6780ec6` (2026-05-09 утро) → дыры в сигнальном потоке часами.
- UTC mismatch в queries → отчёты hourly/daily могли тихо отрезать последние часы.
- Strategy switcher падал каждый час с "connection already closed" — AUTO mode де-факто мёртв 6+ часов.

## Что валидно из старого

- `project_backtest_findings.md` — backtest на чистых исторических OHLCV, не зависел от live багов.
- TP-funnel hit rates на закрытых сделках (relative metric, физика рынка работает).
- Per-symbol ranking (auto-blacklist).
- Memory с lessons learned — самое ценное.

## Как использовать baseline в queries

`stats_baseline_at` — string в `bot_settings`. Чтение:
```python
from psycopg2 import connect
# ...
row = cur.execute("SELECT setting_value FROM bot_settings WHERE setting_name='stats_baseline_at'").fetchone()
baseline_at = row[0]  # '2026-05-10 05:28:55 UTC'
```

Любая SQL для отчётов / KPI / ML retrain должна добавлять:
```sql
AND entry_time >= '2026-05-10 05:28:55'
```

**Существующие endpoints `/api/v2/strategy/<name>` и `/api/v2/overview` пока НЕ применяют этот фильтр автоматически** — нужен отдельный PR если хотим dashboard "post-baseline only" view. Сейчас dashboard показывает ВСЁ, включая pre-baseline мусор. Период-селектор (1h/24h/7d) частично спасает: для 24h/7d мусор уже почти не попадает.

## Что не надо использовать pre-baseline

- Решения о включении REAL.
- Meta-labeler retrain — обучить заново после набора 50+ post-baseline сделок (memory `project_meta_labeler_v1`).
- GA fitness — переоценить на новой выборке.
- Auto-blacklist может содержать pre-baseline артефакты — пересмотреть когда наберётся новая статистика.

## Восстановление если потребуется откат

Все pre-wipe данные лежат в `*_archive_20260510_baseline_v3_clean` таблицах (см. список выше). Для полного отката:

```sql
-- Опасно! Только если Артём явно попросит откат:
INSERT INTO simulated_trades SELECT * FROM simulated_trades_archive_20260510_baseline_v3_clean;
INSERT INTO real_trades SELECT * FROM real_trades_archive_20260510_baseline_v3_clean;
INSERT INTO signals_queue SELECT * FROM signals_queue_archive_20260510_baseline_v3_clean;
INSERT INTO accepted_signals SELECT * FROM accepted_signals_archive_20260510_baseline_v3_clean;
INSERT INTO strategy_statistics SELECT * FROM strategy_statistics_archive_20260510_baseline_v3_clean;
```

Не делать без явного запроса.
