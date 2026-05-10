---
name: Pre-baseline-v3 trading data = мусор, не использовать
description: Всё в trading_bot_v3 БД до 2026-05-10 05:42:10 UTC недостоверно из-за каскада багов; для решений брать только post-baseline
type: feedback
originSessionId: 93067773-cafa-4ab3-b8c6-cf84bdc85eda
---
**Правило**: при любом обращении к торговым данным в `trading_bot_v3` БД (simulated_trades, real_trades, signals_queue, accepted_signals, strategy_statistics) — ВСЕГДА фильтровать `entry_time >= stats_baseline_at` (= **`2026-05-10 05:42:10 UTC`**). Всё что раньше — мусор и для решений не использовать.

**Why:** на Артёма ушло 2026-05-09 — несколько критических багов одновременно искажали данные:

1. WS interim-bar bug → spike-расчёт ломан → сигналы шли в случайные моменты, не репрезентативная выборка.
2. Hard cap двойной счёт (`notional = position × leverage`) → TREND/AGGR позиции $1.43 вместо $50, абсолютные PnL копеечные.
3. WS keepalive bug до коммита `6780ec6` → дыры в сигнальном потоке часами без `_on_close` событий.
4. UTC mismatch (`datetime.now()` локальный против Postgres UTC) → SQL-фильтры тихо отрезали последние ~6 часов данных в отчётах.
5. Strategy switcher падал с "connection already closed" 6+ часов подряд → AUTO mode де-факто мёртв, переключения не происходили.
6. Hardcoded `klines_5m[-6:]` vs `volume_avg_bars=8` → `_check_signal` тихо `return None` на каждом сигнале в момент когда конфиг был выставлен 8.

Артём 2026-05-10 05:42:10 UTC сделал full wipe (TRUNCATE) всех 5 таблиц + сохранил архивы в `*_archive_20260510_baseline_v3_clean`. См. `project_baseline_v3_2026-05-10.md` для полных деталей.

**How to apply:**

- При запросе типа "покажи win rate" / "сколько сделок" / "PnL за месяц" — **сразу читать `stats_baseline_at` из `bot_settings`** и фильтровать. Никогда не отдавать абсолютные числа за весь период без оговорки "post-baseline only".
- Перед любым решением (включить REAL? переключить стратегию? перетренировать meta-labeler? пересмотреть GA params?) — проверять что сделок post-baseline **минимум 50–100** на стратегию. Меньше — недостаточно для выводов.
- При запросе "почему статистика такая" — первая гипотеза: сколько сделок post-baseline? Если мало — ответ "ещё не накопилось".
- Архивные таблицы `*_archive_20260510_baseline_v3_clean` — **только для forensic**, не для статистики/решений.
- Если Артём сам ссылается на старые цифры — деликатно напомнить про baseline.
- Дашборд `/api/v2/strategy/<name>` пока **не фильтрует** по baseline автоматически — Артём это знает; period-селектор (24h/7d) частично спасает, но 30d/all-time тянет мусор.

**Related memories:**
- `project_baseline_v3_2026-05-10.md` — детали wipe + список архивов + SQL для отката.
- `feedback_signal_bar_logic.md` — bar logic фиксы.
- `feedback_hard_cap_double_count.md` — hard cap fix.
- `feedback_dashboard_view_lock.md` — dashboard 502 fix.
- `feedback_dashboard_utc.md` — UTC trap.
- `project_meta_labeler_v1.md` — переобучить ПОСЛЕ 50+ post-baseline trades.
- `project_backtest_findings.md` — backtest на чистых исторических OHLCV (НЕ затронут багами, можно использовать).
