---
name: Wife Tutor Correction-First Format
description: @EnglishTecherTutorBot теперь поправляет ошибку В НАЧАЛЕ ответа (тег [FIX]...[/FIX]), потом продолжает беседу — для голоса и текста
type: project
originSessionId: 8d2f9d7c-3290-489b-addf-b57a4e9806fa
---
2026-05-09: переделан педагогический контракт `wife-english-tutor`.

**Why:** Артём попросил чтобы бот сначала исправлял Лилию (время глагола, артикли, предлоги, слова), потом отвечал на смысл. Старый формат был наоборот — `Note: ...` в конце, и в TTS вообще не озвучивался (avoid Russian in tts-1).

**How to apply:**
- Промпт в `bot/llm.py:30-60` требует `[FIX]english correction[/FIX]` в начале ответа, ТОЛЬКО английский внутри тега (TTS его произносит).
- Парсер `split_reply()` достаёт correction из `[FIX]`, есть legacy-fallback на `Note:` для старой истории в БД.
- TG бот (`bot/tutor_bot.py`): TTS = `correction + ". " + eng`, после голоса text-bubble `Better: {correction}`.
- Web/PWA (`web/app.py`): TTS = тот же формат; фронт `web/static/app.js` рендерит `Better:` бабл ПЕРЕД teacher-баблом.
- Если ошибки нет — `[FIX]` отсутствует, `correction=None`, всё работает как раньше.
- Опечатки Whisper (yers/tree/etc) игнорируются по промпту — фокус на грамматике/tense.

**Edge cases:**
- Если модель регрессирует и снова шлёт `Note: ...` — legacy парсер ловит, но коррекция уйдёт в КОНЕЦ TTS, не вверх. Нужен monitoring если такие случаи участятся.
- Русские объяснения промпт разрешает в самом конце ответа (после английского), не в `[FIX]` — иначе TTS английским голосом будет читать русский.
