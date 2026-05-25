---
name: feedback-signalbot-dead-pg-conn
description: "psycopg2-коннекты (signalbot self.db_conn + tradingbot self.db_conn_ipc) мрут после ~1.5d uptime — записи в signals_queue/accepted_signals/signal-обработка тихо теряются → бот не торгует. Fix задеплоен в обоих ботах (signalbot commit 9d913b9, tradingbot commit 1d4917c) — 2-attempt retry + reconnect."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8d8a9d06-61d1-431c-bd4f-b7be01653cbd
---

**Симптом.** Бот вроде живой (logs идут, EMA-gate работает, сигналы шлются в Telegram), но `signals_queue` и `simulated_trades` не пополняются часами. Артём говорит «не торгует».

**Корневая причина.** В `telegram_bot_runner_v3.py:678` функция `_save_signal_to_db()` падает с `psycopg2.InterfaceError: connection already closed`. Connection помирает после многочасового uptime без reconnect-логики. Лог:
```
⚠️ Error reading strategy from DB: connection already closed, using CONSERVATIVE
💾 SAVING signal to DB: <SYMBOL>
psycopg2.InterfaceError: connection already closed
✅ Сигнал <SYMBOL> отправлен в Telegram
```
Telegram-нотификация бежит после save — поэтому со стороны Артёма «вижу сигнал в чате», а реально его в БД нет.

**How to detect:**
```bash
# Свежие сигналы в БД (должно быть в районе кол-ва "🔥 СИГНАЛ" из логов)
psql ... -c "SELECT COUNT(*) FROM signals_queue WHERE created_at > NOW() - INTERVAL '1 hour';"
# vs кол-во сгенерированных сигналов
journalctl -u bybit-signalbot --since '1hour ago' | grep -c "🔥 СИГНАЛ"
# Если 0 в БД но >0 в логах — это оно.
journalctl -u bybit-signalbot --since '1hour ago' | grep "InterfaceError\|connection already closed"
```

**Workaround (немедленный):**
```bash
systemctl restart bybit-signalbot
# на следующем 5m bar close (00/05/10/15/20...) сигналы пойдут в БД
```
После рестарта ConcurrentSignalBot создаёт свежий connection — работает. Проверено 2026-05-22 06:20 UTC после случая 2026-05-21 13:00 → 2026-05-22 06:17 UTC (≈17h без сигналов в БД, но в логах генерация шла).

**Why:**
- Долгий uptime signalbot'a (~1.5 дня) без reconnect — psycopg2 connection помирает (Postgres `idle_in_transaction_session_timeout`, `tcp_keepalives`, или просто стейл коннект).
- В `_save_signal_to_db` нет try/except с reconnect — exception ловится верхним слоем как warning, сигнал теряется тихо.
- Параллельно `stats_mgr` использует свой pool который переконнекчивается — поэтому tradingbot и dashboard продолжают работать, маскируя проблему.

**Code fix #1 — signalbot 2026-05-22 (commit `9d913b9`):**
- `__init__` кеширует `self._db_params` для reconnect.
- Новый helper `_db_reconnect(reason)` в `telegram_bot_runner_v3.py` — закрывает старый conn (best-effort) + открывает свежий + лог.
- `_save_signal_to_db` обёрнут в 2-attempt retry: catch `(psycopg2.InterfaceError, OperationalError)` → reconnect → retry once. На exhausted retries — `❌ IPC save GIVE UP` (раньше было silent).
- `_get_current_strategy` — тот же паттерн.
- 5 unit-тестов: `tests/test_telegram_runner_db_reconnect.py`.

**Code fix #2 — tradingbot 2026-05-22 (commit `1d4917c`):**
- `main_bot_v3.py:__init__` кеширует `self._ipc_db_params`.
- `_ensure_db_connection` усилен: специфично ловит `(InterfaceError, OperationalError)` → close + reconnect immediately (а не ждать следующего тика).
- Hot-path writers с _ensure_db_connection() guard: `_mark_signal_processed_in_db`, `_log_accepted_signal`, `_update_signal_status`, `_update_signal_acceptance`.
- 2-attempt retry в `_mark_signal_processed_in_db` + `_log_accepted_signal` (по паттерну signalbot).
- 4 unit-теста: `tests/test_main_bot_db_reconnect.py`.

**Code fix #3 — дочерние модули 2026-05-22 (commit `605147e`+ ниже):**
- `statistics_manager_v3.py`: кеш `_direct_conn_params`, новый `_ensure_direct_alive()` (pool-mode no-op, direct-mode ping+reconnect), `_get_conn` self-heal, `_query` обёрнут в 2-attempt retry на dead-conn. **Транзитивно покрывает HourlyReporter + DailyReporter** (они все DB-обращения через stats_mgr).
- `price_monitor_v3.py`: импорт env_config, кеш `_db_params`, `_ensure_db_connection` helper, guards в 3 hot-path методах (`get_last_price`, `_update_ws_price_in_db`, `get_open_position_levels`). На dead conn — REST fallback (read) или silent return (write).
- Тесты: 4 в `test_statistics_manager_reconnect.py` + 3 в `test_price_monitor_reconnect.py`. Full suite 197 pass.
- Verified live: первый `🔄 StatsMgr direct conn reconnected` сработал в dashboard сразу после рестарта.

**TODO (не в фиксе):**
- Healthcheck: если за 30 минут было >5 «🔥 СИГНАЛ» в логе но 0 в `signals_queue` → Telegram-алерт «PIPELINE DEAD». Можно через [[project_hourly_supervisor]].
- Pool-refactor через `database_v3.DatabaseConnector` — не нужно, overkill.

**Связано с:**
- [[feedback_query_write_swallow]] — похожая history (stats_mgr глотал INSERT'ы без commit)
- [[feedback_bybit_ws_keepalive]] — keepalive паттерн но для WS
- [[project_hourly_supervisor]] — мог бы поймать gap, но он смотрит другие метрики
