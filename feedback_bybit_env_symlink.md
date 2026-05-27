---
name: feedback-bybit-env-symlink
description: "/root/gerchik-trading-agent/.env is a symlink to /root/4BotsBybit-Trading/.env — same file, two projects. Adding diverging keys requires either breaking the symlink or introducing differently-named env vars."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4549af2c-3ca5-42b1-8cf2-f9e95b8aeb3c
---

`/root/gerchik-trading-agent/.env` → symlink → `/root/4BotsBybit-Trading/.env`. Один физический файл, два проекта читают один и тот же набор переменных.

**Why:** Артём так настроил намеренно — чтобы DB creds / TG токены не дублировать. Но это означает что если TradingBot и AI-agent должны жить на РАЗНЫХ Bybit ключах, нельзя просто заменить `BYBIT_API_KEY` — оба бота прочитают новое значение.

**How to apply:**
- Если нужны диверг-ключи между двумя проектами — вводить отдельную ENV-переменную в коде того проекта, который должен использовать НЕ-стандартный ключ. Пример: `BYBIT_AI_AGENT_API_KEY` для AI-agent (см. `/root/gerchik-trading-agent/src/env_config.py:bybit_creds()`).
- НЕ редактировать `/root/gerchik-trading-agent/.env` напрямую — это редактирование real-файла `/root/4BotsBybit-Trading/.env` под прикрытием. Backups делать на 4BotsBybit стороне.
- `sed -i` в одной сессии где cwd=4BotsBybit и второй sed без cd — оба sed летят в `/root/4BotsBybit-Trading/.env`. Всегда писать абсолютный путь.
