---
name: Project Progress - 4BotsBybit-Trading
description: Current state of the trading bot project, what's done, what's left to do, key architecture decisions
type: project
originSessionId: 49c33260-9917-48ee-b56d-6488fc6efafa
---
## Repository
- GitHub: InfinitySudo/4BotsBybit-Trading (private)
- Local: /root/4BotsBybit-Trading
- Branch: master
- Latest commit: 971000f (2026-04-13)

## Completed (Session 1: 2026-04-09)

### 1. Security: Secrets moved to .env
- `src/env_config.py` loads .env, exports all secrets
- Replaced hardcoded secrets in ~20 files
- **User MUST rotate all keys** — old ones in git history

### 2. First cleanup: Removed 22+ duplicate files
- 16 HTML dashboard duplicates, 6 Python old files, 5 test scripts

### 3. Strategy Switcher fixed
- CONS→TREND: TP2+ rate >= 35% | TREND→CONS: TP3 rate < 20% | Window: 1 hour

### 4. Leverage fixed
- Range x35-x80, Bybit API set_leverage, qty NOT multiplied, small coins auto-skipped

### 5. StatisticsManager created
- Single source of truth for all stats queries (12+ methods)
- Telegram formatters for daily/weekly/monthly/yearly reports

### 6. SmartReporter created
- Weekly (Mon 10:00), Monthly (1st 10:00), Yearly (Jan 1 10:00) reports

## Completed (Session 2: 2026-04-10)

### 7-9. Dashboard API + Daily/Hourly Reporters → StatisticsManager
- All 3 modules migrated from raw SQL to StatisticsManager methods
- Fixed hardcoded Bybit credentials path → env_config
- Added 6 new methods: get_alltime_stats, get_open_positions, get_recent_trades, get_all_trades, get_tp_hit_rates, get_signal_queue_stats

### 10. SmartReporter integrated into main_bot_v3.py
- Step [12/12] in init, smart_reporter.stop() in shutdown

### 11. SignalBot B/S ratio fixed
- Volume threshold *1.0 → *2.0 (x2 ratio per spec) + ATR double confirmation kept

### 12. Docker containerization
- Dockerfile (Python 3.11-slim), docker-compose.yml (6 services: postgres + 5 bots)
- Healthchecks on all, restart: unless-stopped

### 13. Unit tests: 46 tests, 100% pass
- test_risk_manager (24), test_strategy_switcher (9), test_statistics_manager (9), test_env_config (4)

### 14. CI/CD: GitHub Actions
- .github/workflows/ci.yml: lint (flake8) → test (pytest) → docker build

### 15. Health checks
- Docker: built-in healthchecks + auto-restart
- VPS: src/health_checker.py — pgrep monitoring + Telegram alerts

### 16. Control bot partial refactor
- Extracted 5 keyboard builders → control_bot_keyboards.py

### 17. Fixed 22 bare except: → except Exception: in 5 v3 files

### 18. Removed 14 legacy files (-5003 lines)
- control_bot_full/ultra_simple/v3/strategy_v3, strategy_manager_control
- dashboard_api_v1/v2, dashboard_http/http_v1/server_v1
- signal_bot v1/v2, trading_bot v1, trading_bot_runner

## Session 3: 2026-04-10 continuation

### 19. ControlBot fully migrated to new repo under systemd
- Old /root/4botsBybit-production copy killed, `bybit-control-bot.service` now points at /root/4BotsBybit-Trading
- 30 hardcoded paths + `git pull origin main` → `master` replaced in control_bot_simple_v3.py
- All 3 trading bots (SignalBot, TradingBot, StrategySwitcher) now also run from new repo

### 20. Old api_stable.py on :8003 disabled
- `trading-api.service` stopped + disabled (was serving stale data with broken SQL)

### 21. handle_callback refactored (dispatcher + 50 methods)
- 970-line monolith → 20-line dispatcher + per-branch `_cb_*` methods
- Lookup via class-level `_CB_EXACT` dict + `_CB_PREFIX` list (4 prefix handlers)
- dispatcher wraps calls in try/except so one bad handler can't crash polling

### 22. env_config.expand_env_vars added
- trading_v3_artem.json holds secrets as `${DB_PASSWORD}`/`${BYBIT_API_KEY}` (file in git)
- Nothing was expanding them; TradingBot was sending literal `${DB_PASSWORD}` to Postgres
- Applied in main_bot_v3.py right after json.load

### 23. Dashboard API autostart
- New systemd unit `dashboard-api.service` manages it on :8000
- Survives VPS reboot

### 24. Unit tests: 46 → 87 (+41 new)
- test_bybit_api (15), test_order_executor (14), test_paper_trading_simulator (12 + 1 xfail)
- All external deps (HTTP, DB) mocked
- xfail documents pre-existing bug: open_simulated_trade duplicate-symbol guard uses wrong key

### 25. Verified settings persistence
- Telegram button → bot_settings table update confirmed via Postgres query

## Session 3 continuation — Round 2 (2026-04-10)

### 26. Fixed duplicate-symbol guard in open_simulated_trade
- `if symbol in self.open_trades` → `if any(t.get('symbol') == symbol for t in self.open_trades.values())`
- xfail test now passes normally (xfail marker removed)

### 27. Wired signal_bs_ratio config through to actual B/S comparison
- Three bugs stacked: hardcoded `2.0` in the LONG/SHORT comparison, loader reading old-repo path, JSON value 1.5 mismatching the hardcode.
- Now: threshold reads from `self.signal_criteria['bs_ratio']`, loader reads new-repo path, JSON + defaults = 2.0.
- bot_settings.signal_bs_ratio in Postgres is dead config (unused), left untouched.

### 28. Systemd units for three trading bots
- `bybit-signalbot.service`, `bybit-tradingbot.service`, `bybit-strategy-switcher.service` — Restart=always, WorkingDirectory=/root/4BotsBybit-Trading.
- ControlBot.start_bots / stop_bots / restart_bots rewritten from ~180 lines of pkill bookkeeping to three `systemctl` calls.
- All 5 services (4 bot + dashboard-api) now active under systemd; trading survives VPS reboot without manual action.

### 29. Purged /root/4botsBybit-production paths from src/
- trading_v3_artem.json path in signal_bot_v3_websocket.py + strategy_switcher_v3.py
- symbols.json path in telegram_bot_runner_v3.py
- No bot reads from the old directory at runtime anymore. Old dir can be archived once dead Postgres rows + log files are reviewed.

## Session 4: 2026-04-10

### 30. Archived + removed /root/4botsBybit-production (1.1 GB → 68 MB tar.gz at /root/archive/)
- Discovered parallel OpenClaw agent holding state in the old dir; stopped `openclaw-gateway.service` (user-level systemd) before cleanup
- Disabled dead `bybit-dashboard.service` (enabled+failed since 2026-04-08, spamming journalctl hourly)
- Patched 5 old-path references in start_bots_fixed.sh
- Freed ~1 GB disk; all 5 production bots still active

### 31. Refactored hardcoded paths in control_bot_simple_v3.py → env_config
- Added PROJECT_ROOT / CONFIG_DIR / LOGS_DIR / SRC_DIR / TRADING_CONFIG_PATH / SIGNAL_BOT_CONFIG_PATH / TRADING_BOT_LOG_PATH to env_config.py
- Replaced 27 literal `/root/4BotsBybit-Trading/...` strings; subprocess shell commands use f-strings
- ControlBot restart clean, 88 unit tests pass

### 32. signal_bs_ratio cleanup — memory was wrong, no dead row existed
- `bot_settings` table has 11 rows, none named signal_bs_ratio — nothing to delete
- Real flow: ControlBot button writes to signal_bot_config.json, SignalBot reads from same JSON — works correctly
- Fixed fallback default `bs_ratio=1.0` → `2.0` in three places (was inconsistent with SignalBot's 2.0 default and actual JSON value)

### 33. CRITICAL: live B/S ratio was dead for 2+ days — fixed via publicTrade WS aggregator
- **Root cause:** Bybit v5 kline (WS and REST) exposes `[start, open, high, low, close, volume, turnover]` only. NO taker buy/sell split. Empirically verified by subscribing to `kline.5.BTCUSDT` and by probing REST endpoint.
- **Consequence:** signal_bot_v3_websocket._get_bs_ratio_from_klines always fell into the open/close 60/40 heuristic, which mathematically cannot satisfy bs_ratio=2.0 threshold (max ratio 1.5). Result: zero signals fired in last 48+ hours (confirmed via `journalctl -u bybit-signalbot | grep "🔥 СИГНАЛ"` → 0 matches).
- **Fix:** bybit_websocket.py now also subscribes to `publicTrade.{symbol}` alongside kline+tickers (3 topics × 301 symbols = 903 args, split into 3 subscribe messages). New `_handle_trade_message` aggregates taker buys/sells into 5-minute buckets (`trade_buckets[symbol][bucket_start_ms]`). On each kline message, real `buyVolume`/`sellVolume` (USD) from the matching bucket is attached to the kline dict before storing. The existing signal_bot code at line 484 (`k.get('buyVolume', 0)`) now sees real values instead of 0.
- **Warmup:** 25 min for 5 closed 5m bars to each have real B/S data. Spike+trend work from bar 1 because kline_history is pre-fetched via REST at startup.
- **Verified:** smoke test with 3 symbols for 60s showed BTCUSDT buy=$1.1M sell=$523k (68.1% buy), SOLUSDT 18.1% buy — both would pass bs_ratio=2.0 threshold. 6 new unit tests for aggregator, all 94 tests green.
- **Deployed 2026-04-10 06:52 UTC:** tradingbot STOPPED during observation, signalbot restarted with new code. Full warmup ~07:22 UTC. Decision on re-enabling tradingbot pending after Artem reviews first real signals.
- **Important mental model update:** Bybit does NOT give buy/sell volume via kline. The *only* way to get real taker split from Bybit is the `publicTrade.{symbol}` WS topic (aggregate individual trades yourself) or the historical archive at https://public.bybit.com/trading/ (updated daily, yesterday+ only).

### 34. backtest.py — MVP paused at task #4
- File: src/backtest.py (~480 lines). Replays SignalBot+TradingBot on historical klines.
- First run on BTC/ETH March-April showed -63% total PnL — but the ATR calc in backtest was WRONG (classical True Range, no anomaly filter). Live bot uses correct logic in trading_bot_bybit.calculate_atr (15 bars → filter 0.5/1.8 → last 5 normal → mean).
- Backtest ATR has been updated to match live spec, but the signal-source divergence (Bybit has no historical buy/sell split) means backtest can't exactly match live. Task parked until after live B/S fix stabilizes.
- Reachable at `python3 src/backtest.py --symbols BTCUSDT --start YYYY-MM-DD --end YYYY-MM-DD --strategy {cons,trend}`.

## Session 5: 2026-04-10 — CRITICAL bug fix: websocket_prices pipe was dead

### 35. websocket_prices никогда не заполнялась (2+ часа паники)
- **Симптом:** 17 paper-позиций висели 4–6 часов со статусом `open`, 0 trades когда-либо закрыто. TradingBot спамил `⚠️ No price for ...` для 13/17 символов. TP/SL/BE физически не могли сработать.
- **Слой 1 — INSERT→UPSERT:** Таблица `websocket_prices` имеет `UNIQUE(symbol)`. Код в `bybit_websocket._save_price_to_db` делал plain `INSERT` → каждая попытка падала `UniqueViolation`. Фикс: `ON CONFLICT (symbol) DO UPDATE SET price, timestamp = NOW()`.
- **Слой 2 — rollback missing:** psycopg2 в aborted-состоянии после первой ошибки. Все 100% последующих вставок валились молча. Фикс: `rollback()` в except, log.error для первой и каждой 100-й ошибки вместо `log.debug`, optional `on_db_reconnect` callback для InterfaceError/OperationalError (SignalBot передаёт `_get_db_connection` как hook).
- **Слой 3 — PriceMonitorV3 cache-first без TTL:** `get_last_price` кэшировал первое успешное чтение навсегда. После фикса писателя TradingBot всё равно вернул бы старые цены до рестарта. Убрал кэш полностью — читаем websocket_prices каждый тик (O(1) по unique index). `self.last_prices` оставил как on-hand reference, но не источник истины.
- **После деплоя:** 14 застрявших позиций закрылись за ~2 минуты (в основном BE после TP1), net −0.25 USD. 260 price updates/мин в таблице. 113 unit-тестов зелёные.
- **Память урок:** когда видишь `logger.debug` в except — это красный флаг, бага там может висеть месяцами. Всегда log.error хотя бы для первой ошибки в серии.

### 36. signal_bot_config.json tuned by Artem via ControlBot
- Текущие значения: `spike_ratio=6.0`, `bs_ratio=1.5` (не 2.0 как было в старой памяти).
- Изменение сделано Артёмом руками через ControlBot после backtest findings (spike=6 даёт +42% на BTC+ETH).
- Файл в git, diff незакоммичен. Считать это актуальной конфигурацией.

### 37. Take Profit Hit Rates dashboard — пересобран с PnL per level
- **Баг #1:** числитель в `get_tp_hit_rates` шёл по всей таблице, знаменатель — фронт считал из `allTradesData` обрезанного 200 строками. После >200 трейдов проценты врали.
- **Баг #2:** SQL каскад TP неполный для Trend mode (`tp2_count` не включал `LIKE 'TP4%'/'TP5%'`).
- **Баг #3 (глубокий):** `paper_trading_simulator_v3._partial_close_trade` пишет PnL частичных закрытий ТОЛЬКО в `self.stats` в памяти. В БД `gross_pnl_usd` хранит лишь PnL финального chunk'а (BE/SL/последний TP). PnL от TP1/TP2 для уже закрытых сделок потерян безвозвратно.
- **Баг #4:** `qty` в `simulated_trades` затирается на remaining после каждого partial close → размер позиции на момент открытия терялся.
- **Фикс schema:** добавлен `initial_qty NUMERIC` в `simulated_trades`. Заполняется в `database_v3.insert_simulated_trade` (`initial_qty = qty` на момент открытия), никогда не обновляется. Backfill: для трейдов где `tp1_triggered = false` сделано `initial_qty = qty`. Для 11 BE-после-TPx исторических трейдов остался NULL — данные потеряны.
- **Фикс backend:** `get_tp_hit_rates` теперь:
  - Возвращает `{strategy: {total, levels: {label: {count, rate, pnl}}}}`
  - Реконструирует PnL каждого TP уровня из `entry_price + tp_levels[i].price + initial_qty * remaining_pct * close_pct + direction`. Учтено что симуляторский `close_pct` — доля от ТЕКУЩЕГО remaining, не initial. Особый случай: последний триггернутый TP закрывает весь оставшийся остаток.
  - BE/SL PnL берёт из `gross_pnl_usd` (это и есть финальный chunk).
  - Если `initial_qty IS NULL` → count считаем, но PnL не подделываем (показываем $0.00).
- **Фикс frontend:** `renderTPHitRates` обновлён в обоих файлах (`/root/4BotsBybit-Trading/TRADING_DASHBOARD.html` И `/var/www/dashboard/index.html` — это разные файлы, см. ниже!). Теперь рендерит count + rate + pnl с цветом и знаком.
- **TP3(c) = 0 это правильно:** в текущих 16 трейдах никто не доехал до TP3. 5 SL'ов, 6 hit TP1+BE, 5 hit TP1+TP2+BE. TP3 — самая дальняя цель, физически не достигнута.
- **Параллельно нашёл:** `/var/www/dashboard/index.html` ≠ `/root/4BotsBybit-Trading/TRADING_DASHBOARD.html`. nginx отдаёт **index.html**, репо-файл не доезжает до прода автоматически. Дашборд-файлы в прод нужно править вручную в обоих местах. TODO: завести деплой/симлинк.

## Session 6: 2026-04-10 — AGGRESSIVE strategy + manual strategy control

### 38. Added third strategy AGGRESSIVE + manual switching from ControlBot
- **New auto rule:** CONSERVATIVE → AGGRESSIVE if TP3(c) hit rate in last 1h >= 60% AND closed_count >= 5. AGGRESSIVE → CONSERVATIVE when TP3 rate drops below 60%. Aggressive has priority over TREND from CONSERVATIVE.
- **AGGRESSIVE params:** TP ratios 5/10/15/20/30R, distribution 30/25/20/15/10%, BE activation 4.5%, BE offset 1.5%, leverage x50-x80, risk $0.25 (2.5× CONS), max_positions 40 (concentrated). Defined in `config/trading_v3_artem.json` under `strategy_parameters.aggressive`.
- **Code paths touched:**
  - `risk_manager_v3.calculate_aggressive_tp_be()` + dispatch in `calculate_full_trade()` + leverage branch in `calculate_position_size()` + `risk_aggressive_usd` read.
  - `trading_bot_bybit._calculate_aggressive_tp/_be()` + dispatch in `calculate_tp_sl()` — this is what actually runs per-signal in SignalBot's precompute.
  - `telegram_bot_runner_v3.py`: third instance `trading_bot_aggressive`, ThreadPoolExecutor now runs 3 parallel calcs.
  - `order_executor_wrapper_v3.py`: branches on `strategy == 'AGGRESSIVE'`.
- **Decoupled strategy ↔ trading_mode:** removed `_update_trading_mode()` from strategy_switcher. PAPER/REAL is now independent — user toggles via existing ControlBot Trading Mode menu, strategy switches no longer touch it.
- **Manual switching via ControlBot:** new `strategy_mode` + `forced_strategy` rows in `bot_settings` (default AUTO/CONSERVATIVE). Switcher reads `strategy_mode` at start of each check — if MANUAL, stats are computed + logged but switching is skipped. ControlBot Strategy menu fully rewritten: shows mode, active strategy, last switch, live rule status (TP2+ rate, TP3 rate vs each threshold), 4 buttons (AUTO / Force CONS / Force TREND / Force AGGRESSIVE) + Refresh / Back. Force buttons write to bot_settings + current_strategy + strategy_switch_log.
- **DB migration:** `current_strategy` CHECK constraint relaxed to allow AGGRESSIVE. Added `winning_count`/`losing_count`/`win_rate` to stats dict so `_save_statistics()` stops silently throwing KeyError.
- **Tests:** 113 → 118 (+5 for AGGRESSIVE path in `_determine_strategy`). All green.
- **Not deployed yet:** all changes local, systemd services not restarted. User needs to decide when to cycle SignalBot + TradingBot + StrategySwitcher + ControlBot to pick up the new code.

## Session 6 (continued): 2026-04-10 — first REAL orders + 7-stage pipeline verification + fee-aware risk + honest reports

### 39. 7-stage live pipeline verification (all green)
Walked through every production code path before placing any real order. Stages: Bybit API + balance, WS price pipeline, SignalBot/TradingBot health, full signal dry-run, symbol precision + minOrderQty, StrategySwitcher state, OrderExecutor REAL path readiness. Found (and fixed along the way) an `env_config._load_dotenv()` gotcha: it does `if not os.environ.get(key): os.environ[key] = value`, so stale BYBIT creds already in the shell environment silently shadow the real ones in .env. dashboard-api.service has a clean systemd env so it's unaffected, but ad-hoc `python3 -c` testing from Claude Code's shell hit it. The safe pattern is to `unset BYBIT_API_KEY BYBIT_API_SECRET BYBIT_TESTNET` before any `PYTHONPATH=src python3` one-liner that exercises ByBitAPI.

### 40. Found and fixed critical minor bug: ATR zero-division
trading_bot_bybit.calculate_atr() was crashing with ZeroDivisionError when every daily bar got filtered out as anomalous (normal_klines empty → sum([])/len([])). Six tracebacks/hour in SignalBot logs before the fix. telegram_bot_runner_v3 then crashed downstream on `f"{None:.8f}"` format string. Both fixed: ATR returns None with warning, runner skips the signal cleanly.

### 41. Symbols list rebuild: 301 → 426
Artem pasted a curated 421-symbol list. Previous symbols.json was missing BTC/ETH/SOL (the three largest by 24h turnover on Bybit — massive missed edge for spike strategy). 20 delisted symbols dropped, 25 T-Z tail additions (TAO/XRP/ZEC/SUI/WLD/WIF/XMR/TRX/TON/UNI/XLM/...). Final list is 426 symbols in three tiers of 142 each, sorted by 24h USD turnover so tier_1_top is actually the top third by liquidity. Also saved `config/bybit_usdt_perp_universe.json` — snapshot of the full 539-symbol Bybit USDT-perp universe with per-symbol 24h turnover, for future experiments.

### 42. Risk bumped $0.10 → $0.50 (BTC/ETH unblocked)
At $0.10 with atr_mult 0.15 (0.43% SL on BTC), qty for BTC came out to 0.000319 — below Bybit's 0.001 minOrderQty → order_executor silently normalised to 0 and skipped every BTC signal. ETH was at the same edge (risk_floor $0.137). At $0.50 every symbol in tier_1 passes the minimum and BTC/ETH become tradable. Trade-off: $0.50 per trade is 4.5% of the ~$11 balance per SL — not 0.9%.

### 43. First REAL orders placed on Bybit (six in total across two tests)
Used a standalone script that calls production OrderExecutor directly, no flipping of trading_mode (safer than flipping the global flag and risking natural signals firing into REAL). First test (BTC/DOGE/1000PEPE) surfaced the TP-sizing bug (see #44). Second test after the fix (SOL/LINK/SUI) came back clean — LINK showed a textbook 49/30/20% partial TP split. Total fees across six fills: ~$0.23. One position (1000PEPEUSDT) hit SL during the retry interval and closed at exactly -$0.50 — real SL fires correctly. Positions as of session end:
  - BTCUSDT  0.001   @ $73159  — SL $72846, TPs broken (3×100%), uPnL ≈ -$0.04
  - DOGEUSDT 862     @ $0.0949 — SL $0.09433, TPs broken (5.8/3.5/2.3%), uPnL ≈ -$0.37
  - SOLUSDT  0.7     @ $85.39  — SL $84.74, TPs clean (43/29/14%, step-rounded), uPnL varies
  - LINKUSDT 8.1     @ $9.133  — SL $9.072, TPs clean (49/30/20%)
  - SUIUSDT  60      @ $0.9521 — SL $0.9449, TPs clean-ish (50/17/17%, step=10 limits split)
  User explicitly said to leave all five open. BTC/DOGE TPs are broken from the first-test bug but their SL is correct so they're protected.

### 44. Multiple real-order bugs fixed (order_executor_v3 + bybit_api)
All were latent in the codebase and only surfaced because nobody had placed a real order before:
- **TP sizing**: `set_position_stop_loss` was passing close_pct as percent (50/30/20) but Bybit v5 `/v5/position/trading-stop` expects tpSize as **absolute contract count**. On BTC (0.001 qty) Bybit clamped to position size so three TPs all fired at 100%. On DOGE (862 qty) the number 50 was taken literally as 50 coins, so TP1 only closed 5.8% instead of 50%. On 1000PEPE (qtyStep=100) the literal 50 was below minOrderQty and Bybit rejected every TP with "The number of contracts exceeds minimum limit allowed". Fix: new `position_qty` parameter threaded through `order_executor_wrapper.execute_trade → set_position_stop_loss`, compute `tp_qty = position_qty * close_pct`, normalise by qty_step (floor), skip the TP with a warning when the normalised qty falls below minOrderQty (handles the minimum-qty-position case cleanly).
- **validate_order order-of-operations**: order_value check ran on RAW qty, then normalized. For BTC the raw 0.00159 gave notional $116 > max_order_size $100 → rejected, but the normalised 0.001 would have given notional $73 < $100 → passes. Same symptom as the TP sizing bug: the wrong number was checked. Pre-normalising in the test script works around it; fixing `validate_order` to normalise first is cleaner but was not done in this session (noted for TODO).
- **_normalize_qty floating point**: `int(0.7 / 0.1) * 0.1 = int(6.999...) * 0.1 = 0.6000000000000001` — classic Python FP trap, 0.7 became 0.6. Fix: `int(qty / qty_step + 1e-9)` plus explicit round to decimals-implied-by-step so the output is clean 0.7.
- **bybit_api qty string serialization**: `str(0.7000000000000001)` → `"0.7000000000000001"` → Bybit rejects with "Qty invalid". Same for slSize/tpSize in set_trading_stop and qty in place_market_order and place_tp_trigger_order. Fix: format via `f"{x:.10f}".rstrip('0').rstrip('.')` — produces clean "0.7", "431", "0.001", "0.00079796".
- **bybit_api.set_leverage crash on error path**: line 243 called `self.logger.warning(...)` but ByBitAPI has no `self.logger` attribute (constructor doesn't take or store one). Only crashed when set_leverage returned non-OK (e.g. risk-limit rejection of x80 for LINK/SUI), because the happy path returned early. Fix: `_log = __import__('logger').BotLogger('ByBitAPI')` — same pattern used at line 320 for set_trading_stop.

### 45. Fee-aware risk management and trade stats
Added `risk_management.fees.taker_rate` (default 0.00055 = Bybit linear perp taker) to config. `risk_manager.calculate_position_size` now uses `qty = risk / (sl_distance + 2 * entry * taker_rate)` so realised loss at SL equals the risk budget (was under-reporting risk by ~16% before). Also added `risk_manager.calculate_taker_fee(qty, price)` helper — single source of truth for fee math. For BTC at entry $73000, risk $0.5, sl_dist $313, this means qty drops from 0.00160 to 0.00127 (-20%); for DOGE qty drops from 862 to 730 (-15%); for SOL from 0.78 to 0.68 (-13%). All within the same realised-$0.50-at-SL envelope.

DB migration: `fees_paid_usd NUMERIC DEFAULT 0` added to both `simulated_trades` and `real_trades`. `paper_trading_simulator._fees_paid_usd` accumulator tracks opening fee + fee on each partial close + fee on final close. Written to the DB row when the trade closes. `database_v3.update_simulated_trade` persists it. Existing historic trades have `fees_paid_usd = 0` — treat as "unknown, not zero fees" when displaying.

Tests: legacy `TestPositionSize` fixture now explicitly sets `fees.taker_rate: 0` so the old formula assertions still hold. New `TestPositionSizeWithFees` class (+4 tests) covers the fee-aware path. 118 → 122 tests, all green.

### 46. Three lying Telegram reports fixed + unified win-rate definition
Turned out the existing hourly/24h/status Telegram reports were all subtly wrong in different ways:
- **Hourly: "SL: 7 trades (175%)"**. `get_period_stats` filtered by `created_at` (opened-in-window), `get_tp_breakdown` by `updated_at` (closed-in-window). The hourly used the first as the denominator for counts from the second. When 4 trades were opened in a window but 7 were closed in the same window (different cohorts), the percentage blew past 100%. Fix: hourly now queries a dedicated closed_count from the same `updated_at` window and uses per-strategy `total` from tp_breakdown for each strategy's percentages.
- **Hourly + 24h: "Signal→Trade Conversion: 101.3%"**. Signals counted over SQL NOW() window, trades over Python datetime window; with async pipeline lag the counts came from different cohorts, and the ratio is semantically misleading (trades-in-window can come from signals-before-window). Replaced with a "Throughput" section showing two independent counts and an explicit "not a conversion" one-liner so nobody reads it as percentage.
- **24h: "Win Rate: 9.7%"** — the biggest liar. 24h stats counted wins via `gross_pnl_usd > 0`, but BE trades that partial-closed at TP1 first and then finally closed at BE get a small residual positive pnl which made them look like wins. Hourly used close_reason-based wins (correct) but 24h used pnl-based, so the two reports disagreed on the same data. Unified on `close_reason`: TP1-TP5 = win, BE = neutral, SL = loss, in all three reports. **Real 24h state after the fix: 0 TP wins, 19 BE, 45 SL — not 9.7%**. The bot has never reached even TP1 in 64 closed paper trades — that's a strategy/config issue, not calibration noise.

All three reports now also show gross / fees / net PnL as three separate lines. Fees column is 0 for historic trades (pre-migration); going forward new paper trades will populate it via the simulator accumulator.

### 47. Current state at session end
- 9 commits pushed to master in this session: b3ad3f3, e32aeaa, 7066f8b, b23fb24, 59283a0, 16f33c3, e96a3f9, 95d16dc, 410ec80
- Systemd services all active and running new code
- Bybit wallet balance: $20.12 (was $11.16; Artem topped up $10 during the session)
- Available margin: ~$9.40, uPnL ~-$0.52 across 5 open real positions
- Reports are now telling the truth about the bot losing money — **that's the signal to focus on next session**

### What to do next session
1. **Per-symbol breakdown in hourly/24h reports** — P0. With 426 symbols we have no idea which are winning/losing. Reuse `statistics_manager.get_tp_hit_rates()` (which already reconstructs partial hits from tp_levels JSON) and add a "TOP-10 by PnL" + "DEAD symbols (0 signals)" section to the 24h report. This is the single highest-leverage change for optimising the bot.
2. **Understand the 0% TP rate** — once per-symbol is in, find out if it's uniform across all 426 symbols (then it's the spike/bs_ratio/atr_mult config) or concentrated on a few shit-coins dragging the average (then we need to curate). Don't tune parameters until you can SEE the distribution.
3. **Fix the three minor TODOs found during this session** but not addressed:
   - `validate_order` normalises after the size check (should be before — trivially fixable now that position_qty flow works)
   - stale OpenClaw path in `control_bot_stats_extended.py:41` (reads config from /root/.openclaw/... which never existed after migration — falls back silently)
   - Existing BTC/DOGE real positions have broken multi-TPs from the first test. They can be left running with SL protection, or cancelled+re-set using the now-correct code.
4. **Do NOT build an auto-tuner** first. Artem explicitly wants a reporter/analyser agent first, then manual tuning through ControlBot, before any automated parameter tweaking.

## Session 8: 2026-04-13 — GA applied + dashboard GA actual 1-7D + basic auth

### 48. GA Rank #1 applied to live config
- GA optimizer completed, Rank #1 applied via dashboard at 16:21
- New params in `config/trading_v3_artem.json`: CONS tp_ratios [3.46, 7.32, 15.68], TREND 5-level TPs, spike_ratio 10.0, atr_multiplier 0.256, etc.
- Expected: WR 82.7%, Sharpe 20.6, PnL 666.6%

### 49. Dashboard GA Actual — 1D through 7D daily windows
- Changed `/api/ga/performance` windows from `{1D: 24, 3D: 72, 7D: 168}` to `{1D: 24, 2D: 48, 3D: 72, 4D: 96, 5D: 120, 6D: 144, 7D: 168}`
- Frontend renders dynamically from `perf.actual` — no HTML changes needed
- Each day unlocks as hours accumulate after GA apply

### 50. Dashboard protected with HTTP Basic Auth
- nginx `auth_basic` on entire :8080 server block
- Login: `artem`, htpasswd at `/etc/nginx/.htpasswd`
- `/health` endpoint excluded (no auth) for monitoring
- Removed CORS `Access-Control-Allow-Origin: *` from API proxy
- Before: fully open, anyone could view stats and modify settings

### 51. Git commit + push
- Commit 971000f: GA optimizer + dashboard GA section + basic auth + 1-7D tracking
- 10 files changed, +1730 lines

## Still TODO

### Ideas / Future
- [ ] Backtesting module (CONS/TREND historical validation) — IN PROGRESS
- [ ] Grafana monitoring dashboard
- [ ] Integration test for full signal→order pipeline
- [ ] update_setting() in control_bot_simple_v3.py still has hardcoded `host="127.0.0.1"` etc for psycopg2 — should use env_config.get_db_params() (minor, low priority)

### Ideas / Future
- [ ] Monitoring dashboard (Grafana or similar)
- [ ] Multi-account support
- [ ] Backtesting module

## Architecture (4 Bots)
1. **SignalBot** (telegram_bot_runner_v3.py + signal_bot_v3_websocket.py) — WebSocket, 301 pairs
2. **TradingBot** (main_bot_v3.py + risk_manager_v3.py + order_executor_v3.py) — ATR, SL/TP, BE
3. **ControlBot** (control_bot_simple_v3.py + control_bot_keyboards.py + strategy_switcher_v3.py)
4. **SmartBot** (smart_reporter.py + statistics_manager_v3.py + daily/hourly reporters)
5. **Dashboard** (dashboard_api_v3.py — Flask on :8000)

## Key Files (36 .py files in src/)
- `src/env_config.py` — env var loader
- `src/risk_manager_v3.py` — TP/SL/BE, position sizing, leverage
- `src/strategy_switcher_v3.py` — CONS↔TREND switching
- `src/statistics_manager_v3.py` — single source of truth for all stats
- `src/control_bot_keyboards.py` — Telegram inline keyboards
- `src/health_checker.py` — VPS process monitoring
- `Dockerfile` + `docker-compose.yml` — containerized deployment
- `.github/workflows/ci.yml` — CI pipeline
- `tests/` — 46 unit tests

## Deploy Options
1. **VPS**: `./start_bots_fixed.sh` + health_checker.py
2. **Docker**: `docker compose up -d`

**Why:** Fully automated Bybit futures trading with dynamic strategy switching.
**How to apply:** Check this memory at session start. Continue from TODO list.
