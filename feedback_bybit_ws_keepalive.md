---
name: Bybit WS keepalive trap
description: websocket-client run_forever() без ping_interval приводит к CLOSE_WAIT через ~30 сек на Bybit v5 public stream, callback тихо умирает
type: feedback
originSessionId: fbcba95d-de8d-4157-b95c-f02a54a7cfac
---
`websocket.WebSocketApp(...).run_forever()` без аргументов — Bybit v5 public WS (kline/ticker/publicTrade) рубит коннект за ~30 сек без keepalive. Соединение уходит в CLOSE_WAIT (FIN от сервера, наша сторона не закрыла), `_on_close` НЕ вызывается, reconnect-логика не срабатывает. Callback `on_message` просто перестаёт дёргаться — silent dead.

**Фикс:** `run_forever(ping_interval=20, ping_timeout=10)` — websocket-client сам шлёт RFC 6455 ping'и, Bybit отвечает, коннект живёт.

**Why:** SignalBot замерз 25 апреля 2026 на 32 часа без сигналов после рестарта. Логи писали "WebSocket подключен!" + Auto-init для всех 187 символов, потом тишина. `ss -tnp` показал все Bybit коннекты (`13.249.213.x`) в CLOSE_WAIT. Фикс — `bybit_websocket.py:115` добавлен ping_interval=20.

**How to apply:** Любой долгоживущий websocket-client к Bybit v5 (или любой ws-серверу с idle-таймаутом) должен иметь `ping_interval`. Если бот "active" по systemd, но коннект-логи замерли — `ss -tnp | grep <pid>` первое что смотреть; CLOSE_WAIT = silent dead. На Bybit linear stream timeout ~30s, на других может быть иначе. Для надёжности: `ping_interval=20, ping_timeout=10`.

**Дополнительно:** SignalBot v3 использует `_on_close → time.sleep(5) → subscribe_symbols()` для recovery, но при silent dead `_on_close` не вызывается — поэтому одного reconnect-handler'а недостаточно, нужен именно proactive ping.
