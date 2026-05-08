---
name: Wife English Tutor — план 2026-05-07
description: Артём заказал AI-учителя английского для жены (A1-A2 → разговорный быт в Канаде); репо создан, разработка после voice-tutor fixes и GPU GA
type: project
originSessionId: b0493378-8df7-4334-bf78-c554bd77a27c
---
**Кто пользователь:** жена Артёма, A1-A2 beginner. Цель — свободно говорить в быту в Канаде (соседи, магазин, врач, школа). Боится "школьного" подхода — нужен мягкий учительский тон, не прокурорский.

**Repo:** `https://github.com/InfinitySudo/wife-english-tutor` (private), local `/root/wife-english-tutor/`
**Bootstrap commit:** 927cc18 — PLAN.md + dir layout, без кода ещё

**Главное отличие от voice-tutor:**
- Всегда отвечает на английском, даже если ввод по-русски
- Inline gentle correction с пояснением по-русски ("Note: ты сказала *go to home*, правильно *go home* — потому что home без артикля")
- Mistake log + spaced repetition
- Lesson mode (scenarios: at the doctor, in shop, parent meeting)
- Учительский голос (попробовать `shimmer` или клонирование XTTS)

**Платформа:** TG bot + PWA web (общая БД прогресса)

**Stack:**
- LLM: Claude Sonnet 4.6 для педагогики, Haiku для коротких реплик, qwen2.5 fallback
- STT: OpenAI Whisper → faster-whisper local после ПК1 готова
- TTS: OpenAI tts-1 → XTTS-v2 local
- DB: SQLite (mistakes, vocab, lessons, lesson_progress)

**Открытые вопросы (Артём решит):**
- Bot username (`@WifeEnglishTutorBot`?)
- Web URL (`english.constantwrestling.cloud`?)
- Голос — `shimmer` vs `alloy` vs клонирование
- Время daily reminder
- Платный продукт ли в перспективе (сейчас личный)

**Roadmap:**
1. ✅ PLAN.md + repo (2026-05-07)
2. ✅ MVP LLM-ядро (2026-05-08, a8e9903): claude_client + teacher persona + DB + CLI smoke test
3. ✅ TG bot wiring (2026-05-08, d8b0d08): /start /level /mistakes /reset /help + text + voice handlers; voice-only reply on voice-input + correction в отдельном bubble; openai whisper-1 + tts-1 (shimmer); WET_ALLOWED_TG_IDS allowlist
4. ✅ Web PWA MVP (2026-05-08, 20fda9b): FastAPI /api/turn /api/state /api/level /api/reset; TG initData HMAC auth; 3-file SPA с light/dark theme; uvicorn 127.0.0.1:8765; voice через web TODO
5. ⏳ Mistake log spaced repetition (v0.2)
6. ⏳ Lesson mode + roleplay (v0.3)
7. ⏳ Pronunciation feedback (v0.3)

**КРИТИЧЕСКИ:** не fork voice-tutor! Извлечь общие модули (STT, TTS, OAuth, speaker, FastAPI базу) в shared package, иначе багфиксы делать в двух местах.

**Текущее состояние shared-кода (2026-05-08):**
- `bot/claude_client.py` ДУБЛИРУЕТ voice-tutor/bot/llm.py:1-180 (OAuth+fallback)
- `web/auth.py` ДУБЛИРУЕТ voice-tutor/web/auth.py (TG initData HMAC)
- TODO когда оба проекта стабильны: переехать в `/root/shared/{claude_client,tg_auth}.py`
- Запуск через voice-tutor venv: `/root/voice-tutor/.venv/bin/python -m bot.tutor_bot` или `... uvicorn web.app:app --port 8765`
- Schema/persona/TG handlers/static — app-specific, не делятся.

**Endpoints / порт:**
- TG bot: long polling, нужен WET_TG_TOKEN от BotFather (Артём пока не создал @Teacher1Bot)
- Web: 127.0.0.1:8765 (nginx reverse proxy сделать на teacher1.constantwrestling.cloud при готовности)
- Dev escape: WET_DEV_TG_ID=42 в env пропускает HMAC auth для локального теста

**Тестировать через:** `cd /root/wife-english-tutor && /root/voice-tutor/.venv/bin/python -m bot.cli "your sentence"` (используем voice-tutor venv, anthropic 0.97.0).

**Контракт LLM-ответа:** EN body + optional last line `Note: ... ` (RU explanation). `bot.llm.split_reply()` парсит обратно в (english, correction). Категории: articles, tenses, prepositions, word_order, vocabulary, pronunciation, plural_singular, agreement, other.