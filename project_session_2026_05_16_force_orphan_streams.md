---
name: session-2026-05-16-force-orphan-streams
description: "Marathon trading-truth session — SL/FORCE bucket, orphan safety nets, scorecard Sharpe fix, dashboard real defaults, gerchik pyramid bug fix, Stream B (AI-agent) added"
metadata: 
  node_type: memory
  type: project
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

Session 2026-05-16 — 11 commits across 2 repos, 302 tests green.

## Что было сломано (root causes)

1. **`_infer_close_reason` fallback** (`order_executor_wrapper_v3.py`) метил `pnl≤0 + no SL match` как `'SL'`. 70%+ real "SL" были на самом деле `'FORCE'` (BE-trail desync, batched closes, etc.). 46/76 backfilled.
2. **BE-trail рассинхрон** — `_maybe_move_be_real` двигал Bybit-SL на `entry+0.1%`, но `sl_price` в DB оставался ATR-distance → `_infer_close_reason` не матчил → false-FORCE.
3. **Logger UTC label** — `datefmt='... UTC'` hardcoded, но `asctime` использовал local time (MDT). 6h дрейф в логах. Fix: `formatter.converter = time.gmtime`.
4. **Scorecard Sharpe** — на $-PnL (не returns), `sqrt(N)` pseudo-annualize, min 2 точки. Давало −441. Fix: daily returns, sqrt(365), min 5 точек.
5. **Orphan positions** — 4 на Bybit, не в DB ($79 notional, FARTCOIN без SL). Reconciler не проверял reverse Bybit→DB.
6. **Dashboard defaults** — Excursion/Funnel/Heatmap/Per-Symbol дефолтили на `paper` хотя весь sub1 уже на real.
7. **deploy_dashboard.sh** копировал только `TRADING_DASHBOARD.html → index.html` (v1). `index_v2.html → v2.html` (v2) **не копировался** — все правки v2 не доходили до nginx-webroot.
8. **`_ensure_real_trades_compat_view`** при startup пересоздавал view со старой схемой (без peak/trough/close_source). Перетирал ручные ALTER'ы.
9. **gerchik-trading-agent pyramiding bug** — `journal.has_open_on_symbol(symbol)` default `mode='PAPER'`, signal_engine звал без `mode=` → не видел открытый REAL → re-entry. Bybit One-Way агрегировал, DB пухнул. PnL inflated 3.4× (XRPUSDT: DB $93.37, Bybit $27.57).
10. **Stream C label "our agent"** — путаница: на самом деле это main TradingBot (sub1), не AI-agent.

## Что починили (по файлам)

`/root/4BotsBybit-Trading/`:
- `src/order_executor_wrapper_v3.py` — `_infer_close_reason` → tuple (reason, source); BE-trail синкает sl_price; orphan/no-SL reverse-loop + TG-alert with 1h cooldown; SL post-place verification (3 retries → alert, без auto-close per Артём); `sl_triggered=True` only when `reason=='SL'` (исключает FORCE).
- `src/database_v3.py` — `insert_real_trade` 3× retry + dead-letter `failed_real_inserts` JSONB table + TG-alert.
- `src/main_bot_v3.py` — STEP 1B dust filter (`qty × current_price < $2` skipped).
- `src/dashboard_api_v3.py` — view SQL пересоздаёт с peak/trough/close_source; excursion/funnel/heatmap/scorecard добавлен `source=paper|real`; Stream B endpoint sources Bybit sub3 truth (windowed 7d for closed-pnl 90d limit); `_ensure_real_trades_compat_view` SQL обновлён; scorecard Sharpe рефакторен.
- `src/logger.py` — `formatter.converter = time.gmtime`.
- `src/telegram_notifier_v3.py` — `send_alert(text)` module-level helper.
- `src/statistics_manager_v3.py` — FORCE bucket в funnel `force_count/force_pnl`.
- `src/strategy_switcher_v3.py` — SQL `LIKE 'SL%' OR = 'FORCE'` (поведение свитчера не менялось).
- `index_v2.html`, `TRADING_DASHBOARD.html` — FORCE chip/colour, Stream B card, MFE source toggle, heatmap mode dropdown, per-symbol Mode=Real default.
- `scripts/deploy_dashboard.sh` — bash assoc array копирует **обе** пары (v1+v2).

`/root/gerchik-trading-agent/`:
- `migrations/011_pyramid_tracking.sql` — `+bybit_order_id`, `+bybit_order_ids`, `+add_on_count`, `+first_entry_price`, partial idx на open rows.
- `src/journal.py` — `has_open_on_symbol` default `mode=None` (scans both); + `get_open_trade_on_symbol_mode`, `append_to_open_trade` (weighted-avg entry).
- `src/signal_engine.py` — pyramid routing: same-mode same-dir → append (max 3 add-ons); opposite-mode → skip; opposite-dir → skip.
- `src/real_executor.py` — `open_trade` записывает `bybit_order_id`; новая `append_real(qty)` для add-on.

## Архитектура потоков (Streams)

| Sub | UID | Bot | Table | Stream label на дашборде |
|---|---|---|---|---|
| sub1 | 563399107 | main TradingBot (CONS/TREND/AGGR) | `real_trades` | **💰 Main TradingBot (sub1)** ← было "Stream C — our agent" |
| sub2 | 563470305 | Gerchik copy + signals_bot | `gerchik_copy_trades` | **📥 Stream A — Gerchik copy** |
| sub3 | 539929753 | AI-agent (gerchik-trading-agent main) | `gerchik_trades` | **🤖 Stream B — AI-agent** (NEW, Bybit truth) |

Stream B берёт **напрямую с Bybit sub3 closed-pnl** (от 2026-05-15 миграции), а не из DB — потому что `gerchik_trades` имел inflated PnL до сегодняшнего pyramid-fix.

## Решения Артёма (закрепить)

- **TREND отключён** через Risk Officer (`strategy_mode=MANUAL`, `forced=CONSERVATIVE`) — потерял −$9.80 на 21 trades с WR 4.8%. Не торгует до явной отмены.
- **BE-параметры остаются 0.49/0.1** (`be_activation_pct/be_price_offset_pct` для всех 3 стратегий в `strategy_parameters` JSON). What-if на paper показал что повышение activation → −$84..−146 net.
- **MFE-калибровка пока на paper**, real слишком мало точек. Source toggle добавлен — можно переключить когда накопится 200-300 real-трейдов.
- **DB не чистить** — Stream B/Bybit cross-check уже как truth source. История остаётся.
- **Auto-import orphan = НЕТ** (только TG-alert).
- **SL verify fail = НЕТ auto-close** (только alert, позицию оставляем открытой).
- **Pyramiding нужен** (gerchik), но с правильным учётом (одна Bybit position = одна DB row). Max 3 add-on'а.
- **WLFI −$1052** — это ручной успешный трейд Артёма, не bot (Bybit considers как loss из-за asymmetric closing — игнорируем).

## Что НЕ делалось (если спросят)

- Не меняли `tol` в `_infer_close_reason` (1%) — strategy не трогаем.
- Не чистили исторические 6 XRP-rows в `gerchik_trades` — paper history.
- 21 closed TREND в `real_trades` НЕ удалены (вернули из `real_trades_archive_trend_20260516` после моей ошибки) — Артём хотел разобраться кто что делал, не удалять.
- gerchik bug fix НЕ переразмечает старые 6 XRP rows — Stream B на дашборде уже показывает Bybit truth.

## Связанные memory ноды

- [[feedback-real-trades-truth]] — Bybit truth pattern, теперь содержит SL/FORCE split
- [[feedback-dashboard-view-lock]] — lock_timeout=5s + idle_in_tx_session_timeout=60s pattern
- [[feedback-no-routine-confirms]] — карт-бланш на рутину
- [[feedback-auto-push-default]] — после commit'а сразу push
- [[project-bybit-3sub-architecture]] — три-sub-аккаунта (теперь дополнено labels A/B/C)
- [[feedback-bybit-env-symlink]] — общий `.env` файл с разными credentials
- [[project-mfe-calibration]] — MFE TP-tuning, теперь имеет source toggle
- [[project-hybrid-mode]] — per-strategy paper/real routing
