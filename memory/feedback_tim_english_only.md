---
name: Tim — английский only
description: Все материалы, строки бота, документы для Тима — только English. Тим не понимает русский.
type: feedback
originSessionId: b0493378-8df7-4334-bf78-c554bd77a27c
---
Тим (Tim Todorov) НЕ говорит и НЕ читает по-русски. Все его user-facing materials — строго English:

**Why:** Тим — клиент Артёма, говорит только на английском. Любые русские слова в его боте/документах = он не поймёт + выглядит непрофессионально.

**How to apply:**
- ЛЮБЫЕ строки в bot.py, cards.py, help_text.py, что Тим увидит → English
- docs/tim_user_guide.md, docs/agent_plan.md, docs/agent_persona.md → English
- Email drafts, calendar events, search prompts → English
- Code comments которые описывают user-facing behavior → English (для поддерживаемости)
- Внутренние комментарии разработчика которые Тим никогда не увидит → можно RU
- Commit messages → можно RU (это для нас)
- Memory файлы (этот) → RU как обычно

**Repo:** InfinitySudo/emails-optimization — НЕ пихать туда русский в user-facing
**Bot:** @TimsBot (`emails-bot-tim.service`)

**Артём указал:** 2026-05-08, при работе над agent_plan.md я по привычке писал на русском. Артём поправил, я перевёл.