---
name: Telegram emoji-prefix breaks CommandHandler
description: KeyboardButton "📅 /daily" не дёргает CommandHandler в python-telegram-bot, и vocab/quiz-сессия залипает
type: feedback
originSessionId: 20cd5d72-84e3-40a0-84f1-0e561eea6007
---
В python-telegram-bot `CommandHandler` срабатывает только если `entities[0].type == BOT_COMMAND` И `entities[0].offset == 0`. То же самое `filters.COMMAND` (по умолчанию `only_start=True`). Кнопка `KeyboardButton("📅 /daily")` шлёт текст `"📅 /daily"` — bot_command entity на offset≈3, поэтому:

- `CommandHandler` не срабатывает (offset != 0).
- `MessageHandler(filters.TEXT & ~filters.COMMAND, ...)` ВСЁ РАВНО срабатывает (`~filters.COMMAND` = True, потому что first.offset != 0).
- Сообщение приходит в общий handle_text и трактуется как обычный текст / ответ на квиз / chat.

**Why:** В CELPIP-боте Лили это вызвало "залип": в активной vocab-сессии каждый тап на `📅 /daily` грейдился как неправильный ответ, и она не могла сменить урок. Чинил 2026-04-29: добавил re-dispatch внутри handle_text через COMMAND_REGISTRY (находит BOT_COMMAND на любом offset → лукапит callback → клирит state → дёргает) + group=-1 pre-handler чтобы прямой `/cmd` тоже чистил сессию + `/stop` команду.

**How to apply:**
- При создании `KeyboardButton` либо ставь `/cmd` на offset 0 (`KeyboardButton("/daily")` или `KeyboardButton("/daily 📅")`), либо обеспечь fallback-роутинг через MessageHandler.
- Любой долгоживущий per-user state (vocab_session, quiz, FSM) — обязательно делать `/stop` и pre-clear на любую команду группы -1, иначе пользователь застрянет.
- При код-ревью telegram-ботов проверять: есть ли способ выйти из сессии без перезапуска бота / без полного дрейна очереди.
