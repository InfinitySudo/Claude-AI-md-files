---
name: tg-persistent-keyboard
description: "В TG-ботах с tutor pattern reply_markup=QUICK_KB надо вешать на free-chat ответы, а не только на /start — иначе юзер, который пишет сразу 'привет' без /start, не увидит кнопок"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 86b3e61d-1a05-403f-96c7-b266738e425f
---

В `wife-english-tutor` / `son-french-tutor` / любых tutor-ботах с `QUICK_KB = ReplyKeyboardMarkup([...], is_persistent=True)`: прикреплять `reply_markup=QUICK_KB` нужно в **free-chat reply path** (`on_text` / `on_voice` finishing reply), а **не только в `/start` и `/help`**.

**Why:** Артём (2026-05-11) сказал "у жены нет кнопок". Причина: жена/он никогда не делали `/start` — а keyboard прикреплялся только там. После добавления `reply_markup=QUICK_KB` к `reply_text(full_reply, ...)` и `reply_voice(voice=f, ...)` в финальной точке free-chat, keyboard цепляется при любом первом сообщении и держится (`is_persistent=True` в TG Bot API 6.3+).

**How to apply:** В новых tutor-ботах ставить keyboard в `reply_voice`/`reply_text` финального ответа на свободное сообщение, а не полагаться на `/start`. Связано с [[feedback_telegram_keyboard_emoji]] (без emoji-префикса в KeyboardButton — иначе CommandHandler не срабатывает).

**Также:** `set_chat_menu_button(MenuButtonWebApp)` **заменяет** стандартную кнопку "Меню" со списком команд. Если бот хочет показывать и WebApp, и список команд — нужны два решения: `MenuButtonWebApp` слева (≡) + persistent ReplyKeyboard внизу. Telegram не показывает одновременно WebApp menu button и commands list через одну кнопку ≡.

**Якоря:** [[project_son_french_tutor]], [[project_wife_english_tutor]], [[feedback_telegram_keyboard_emoji]]
