---
name: Bybit WS keepalive + supervisor
description: websocket-client run_forever() требует ping_interval + supervisor-loop + idle watchdog — иначе SignalBot периодически замирает silent
type: feedback
originSessionId: fbcba95d-de8d-4157-b95c-f02a54a7cfac
---
Bybit v5 public WS (kline/ticker/publicTrade) роняет idle-коннекты за ~30s. Без защиты `on_message` тихо перестаёт дёргаться — процесс активен, сигналов нет. У SignalBot такие тишина-инциденты случались минимум дважды: 25 апреля 2026 (32h) и 8 мая 2026 (12h).

**Три слоя защиты, все нужны (`/root/4BotsBybit-Trading/src/bybit_websocket.py`):**

1. **`run_forever(ping_interval=20, ping_timeout=10)`** — proactive RFC 6455 keepalive. Без этого Bybit рубит коннект за ~30s, и при half-open TCP `_on_close` не вызывается совсем (FIN/RST не приходит).

2. **Supervisor-loop в `_run_websocket`** — внешний `while self.running:` цикл с exp backoff (5→60s), сам пересоздаёт `WebSocketApp` через `_build_ws()` после каждого выхода из `run_forever`. **`_on_close` НЕ должен звать `subscribe_symbols`** — это плодило threads и ломало reconnect-цепочку при первой transient-ошибке (это и был сценарий 8 мая: `_on_close → subscribe_symbols → return False → end`). До 9 мая 2026 был именно такой рекурсивный код.

3. **Idle watchdog daemon-thread** — каждые 30s проверяет `time.time() - _last_message_ts`; если >90s тишины при `connected=True` — зовёт `self.ws.close()`, supervisor подхватит. Защищает от silent half-open, когда даже ping не помог. `_last_message_ts` обновляется первой строкой `_on_message`.

**How to apply:**
- Любая правка `bybit_websocket.py` в reconnect-области должна сохранять все три слоя.
- Если SignalBot снова замолчал: `ss -tnp | grep $(pgrep -f telegram_bot_runner_v3)` — много CLOSE_WAIT к 18.161.* / 13.249.* = WS layer мёртв. `tail logs/signal_bot_runner_v3.log` — ищи `🔄 WS supervisor: reconnect #N` (значит supervisor работает) или `🐶 watchdog: …s тишины` (значит watchdog поймал half-open). Если ни того ни другого и тишина >2 минут — все три слоя сломаны, баг новый.
- Любой долгоживущий websocket-client к Bybit (или любому idle-timeout серверу) должен иметь все три слоя; одного `ping_interval` недостаточно.
