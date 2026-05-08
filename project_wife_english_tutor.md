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
2. ✅ MVP LLM-ядро (2026-05-08, commit a8e9903): claude_client + teacher persona + DB + CLI smoke test проходит на 4 кейсах
3. ⏳ TG bot wiring (handlers, voice loop, /level, /mistakes commands)
4. ⏳ Web PWA (clone из voice-tutor)
5. ⏳ Mistake log spaced repetition
6. ⏳ Lesson mode + roleplay

**КРИТИЧЕСКИ:** не fork voice-tutor! Извлечь общие модули (STT, TTS, OAuth, speaker, FastAPI базу) в shared package, иначе багфиксы делать в двух местах.

**Текущее состояние shared-кода (2026-05-08):**
- `bot/claude_client.py` ДУБЛИРУЕТ voice-tutor/bot/llm.py:1-180 (OAuth+fallback). Sonnet→Haiku fallback chain работает, проверено rate-limit-кейсом.
- TODO когда оба проекта стабильны: переехать в `/root/shared/claude_client.py`, оба проекта импортят оттуда.
- Schema/persona/TG handlers — app-specific, не делятся.

**Тестировать через:** `cd /root/wife-english-tutor && /root/voice-tutor/.venv/bin/python -m bot.cli "your sentence"` (используем voice-tutor venv, anthropic 0.97.0).

**Контракт LLM-ответа:** EN body + optional last line `Note: ... ` (RU explanation). `bot.llm.split_reply()` парсит обратно в (english, correction). Категории: articles, tenses, prepositions, word_order, vocabulary, pronunciation, plural_singular, agreement, other.