---
name: dexclaud-bridge-bot
description: "TG-бот @DexClaudCodAIBot — bridge для отправки уведомлений Артёму из моих скриптов. Токен в `/root/4BotsBybit-Trading/.env` как `CLAUDE_BRIDGE_BOT_TOKEN`, chat_id Артёма из `CLAUDE_OPERATOR_CHAT_ID` (fallback `TELEGRAM_CHAT_ID=504609639`)."
metadata: 
  node_type: memory
  type: reference
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Update 2026-05-16:** этот же бот @DexClaudCodAIBot стал full Claude Code agent (см. [[dexclaud-plan-first]]) — `/root/claude-telegram-bot/claude_bot.py` с tools/vision/voice + create_plan/update_progress. Этот memory описывает ТОЛЬКО bridge-режим (sendMessage из других скриптов без интеракции).

**Что:** Готовый канал слать прогресс/факты Артёму в TG без открывания собственного бота.

**Как:**
```python
import os, requests
from dotenv import load_dotenv
load_dotenv('/root/4BotsBybit-Trading/.env')
token = os.getenv('CLAUDE_BRIDGE_BOT_TOKEN')
chat = os.getenv('CLAUDE_OPERATOR_CHAT_ID') or os.getenv('TELEGRAM_CHAT_ID')
requests.post(f'https://api.telegram.org/bot{token}/sendMessage',
              json={'chat_id': chat, 'text': 'message here'})
```

**Когда использовать:** артём в течение долгой сессии просил скинуть факты в "@DexClaudCodAIBot" — это про этот же bridge. Сейчас активный path для длинных reports / "сохрани результат".

**Caveats:**
- Markdown в TG: ставь `parse_mode='Markdown'` если нужно. Без него text plain.
- Длина message ≤ 4096 chars. Длиннее — разбивай на части.
- `disable_web_page_preview=True` для compact look когда в тексте URL.
- Не зови с одной и той же сессии слишком часто — TG rate limit 30 msgs/sec/bot.
