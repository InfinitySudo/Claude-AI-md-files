---
name: project-session-2026-05-25-wet-games-select
description: "WET 2026-05-25 — multi-select phrase в reader+chat, игра /play (Words+Letters), корректор-SONNET, no-cache + /reload"
metadata: 
  node_type: memory
  type: project
  originSessionId: 9ef7b3ce-b786-4fb4-851f-4508e0accb52
---

Сессия `wife-english-tutor` 2026-05-25 (commit `faefabe`):

**1. Корректор правит ВСЕ предложения**
- `bot/llm.py`: `reply_for_turn` + `reply_for_turn_stream` дефолтом `MODEL_SONNET` (был HAIKU). max_tokens 1200→2000.
- Промпт: добавлен ПРОТОКОЛ ПРОВЕРКИ (шаг 1-4: разбей→оцени→[FIX]→ответ) + пример с 5 предложениями = 5 [FIX].
- Запись: [[feedback_wet_corrector_sonnet]] — НЕ переключай обратно на HAIKU без согласия.

**2. Multi-word selection (reader + chat)**
- `read.html`: режим «✂️ Фраза» в шапке главы — тапаешь несколько слов, плавающая пилюля «Save»; плюс native text selection (long-press) тоже показывает FAB.
- `app.js` + `style.css`: выделение в `.bubble.teacher` (ответы Алёны) → плавающая «Save phrase» → `/api/phrase/save`.
- Backend в `reading.py`: `lookup_phrase` + `save_phrase_to_vocab` (фразы кэшируются в `word_lookups`, идут в `vocab_reviews` как обычные слова).

**3. Игры на `/play`**
- `play.html`: tabs **📝 Words** (собрать предложение из токенов) и **🔤 Letters** (собрать слово из букв; дистракторы 0/2/3/4 по уровню A1/A2/B1/B2).
- Endpoints: `GET /api/game/scramble?level=...`, `GET /api/game/letters?level=...`.
- Источник: реальные предложения из `book_chapters` того же уровня, слова из `word_lookups`; fallback на curated-список.
- Кнопка **📚 Add to vocab** в обеих играх. Счёт/streak/played в localStorage.
- Drawer-кнопка `🎲 Word Games`.

**4. Cache-busting (TG WebView кэшировал HTML)**
- `app.py`: `/`, `/read`, `/play` отдают `Cache-Control: no-store`.
- `tutor_bot.py`: команда `/reload` шлёт 3 свежих ссылки с `?t=timestamp`; menu-button бампается на старте.
- Жена не находит mini-app в TG cache UI — потому что Telegram прячет WebApp-кэш. `/reload` — единственный надёжный способ обновить без полной чистки.

**5. UI на английском**
- `/play` целиком на английском (Build the sentence / Build the word / Check / Undo / Hint / Next / Add to vocab); русским остаётся только translation_ru как подсказка в letters-игре.

**Фикс прогресса книг (a6fa68f):**
- Жена жаловалась — прогресс не двигается. Причина: `set_book_progress` существовал в reading.py, но из read.html никто не звал → таблица `book_progress` не обновлялась.
- Добавил `POST /api/books/{slug}/progress` с MAX-семантикой (возврат к ранней главе не сбрасывает счётчик).
- `read.html` `showChapter()` теперь зовёт `saveBookProgress` при каждом открытии + патчит локальный `state.progress` для немедленного обновления полоски в списке книг.

Связано: [[project_progress]], [[feedback_wet_corrector_sonnet]], [[feedback_pwa_stale_bundle]].
