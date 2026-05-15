---
name: Wife English Tutor — план 2026-05-07
description: AI-учитель английского @EnglishTecherTutorBot. Persona Алёна Николаевна (shimmer). Latency pipeline ported 2026-05-12 (Haiku + streaming TTS + STT race). Max_tokens 1200 — развёрнутые ответы (Lilia просила полнее).
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

**Stack (2026-05-12):**
- LLM: Claude **Haiku 4.5** для всего (был Sonnet); `reply_for_turn` default переключен. max_tokens **1200** (было 700) — жене нужны развёрнутые ответы (4-6 предложений, до 8 на запрос объяснения). Persona prompt updated.
- Latency: streaming TTS pipeline = same as son-french-tutor; см. [[project_tutor_latency_pipeline]]. Backend turn ~2-4s.
- STT: OpenAI Whisper → faster-whisper local после ПК1 готова
- TTS: OpenAI tts-1 → XTTS-v2 local
- DB: SQLite (mistakes, vocab, lessons, lesson_progress)

**Открытые вопросы (Артём решит):**
- Bot username (`@WifeEnglishTutorBot`?)
- Web URL (`english.constantwrestling.cloud`?)
- Голос — `shimmer` vs `alloy` vs клонирование
- Время daily reminder
- Платный продукт ли в перспективе (сейчас личный)

**Roadmap (всё отгружено 2026-05-08 в одну сессию):**
1. ✅ PLAN.md + repo (2026-05-07)
2. ✅ MVP LLM-ядро (a8e9903): claude_client + teacher persona + DB + CLI smoke test
3. ✅ TG bot wiring (d8b0d08): text + voice handlers, voice-only reply, allowlist
4. ✅ Web PWA MVP (20fda9b): FastAPI + 3-file SPA, TG initData HMAC auth
5. ✅ Push-to-talk голос в PWA (602c7d1): MediaRecorder + /api/voice + auto-play TTS
6. ✅ Avatar UI (5d551d1): SVG-учительница, состояния idle/listening/thinking/speaking/happy, рот синхронизирован с TTS audio events
7. ✅ Streaks + reminders + Progress dashboard (f2b543e): hourly cron 8/12/18 local, /api/progress, 14-day strip, category bars
8. ✅ Achievement badges (35c812e): 10 milestones (turns/streak/fixes/explorer); toast + grid в modal
9. ✅ Pronunciation feedback (4926d81): difflib word-diff на Whisper-транскрипте; "Practice" кнопка под Note bubble; цветной diff (green/red/dotted)
10. ✅ Daily digest 21:00 (df9d68d): TG-резюме дня, top 3 категории ошибок, streak-статус
11. ✅ Vocab spaced repetition (22ff072): Haiku auto-extract из teacher reply, Leitner box 1/3/7/14/30 дней, flashcard UI

**КРИТИЧЕСКИ:** не fork voice-tutor! Извлечь общие модули (STT, TTS, OAuth, speaker, FastAPI базу) в shared package, иначе багфиксы делать в двух местах.

**Текущее состояние shared-кода (2026-05-08):**
- `bot/claude_client.py` ДУБЛИРУЕТ voice-tutor/bot/llm.py:1-180 (OAuth+fallback)
- `web/auth.py` ДУБЛИРУЕТ voice-tutor/web/auth.py (TG initData HMAC)
- TODO когда оба проекта стабильны: переехать в `/root/shared/{claude_client,tg_auth}.py`
- Запуск через voice-tutor venv: `/root/voice-tutor/.venv/bin/python -m bot.tutor_bot` или `... uvicorn web.app:app --port 8765`
- Schema/persona/TG handlers/static — app-specific, не делятся.

**Endpoints / порт:**
- TG bot: **@EnglishTecherTutorBot** (Teacher1Bot был занят), long polling, токен в .env
- Web: **https://teacher1.constantwrestling.cloud** (Let's Encrypt, certbot auto-renew), nginx → 127.0.0.1:8765
- MiniApp: кнопка "Open Tutor" уже подцеплена в боте через setChatMenuButton
- Allowlist: `WET_ALLOWED_TG_IDS=504609639,1356240185` (Артём + жена; chat_id жены = 1356240185, добавлен 2026-05-08)
- Dev escape: `WET_DEV_TG_ID=42` в env пропускает HMAC auth для локального TestClient

**systemd сервисы:**
- wife-english-tutor.service — TG bot (long polling)
- wife-english-tutor-web.service — uvicorn 127.0.0.1:8765
- wife-english-tutor-reminder.timer — hourly, slot 8/12/18 local
- wife-english-tutor-digest.timer — hourly, slot 21:00 local

**TG команды:** /start /level /streak /badges /vocab /mistakes /reset /help
**Web кнопки:** Vocab, Progress, Patterns, Reset chat
**Аватар:** SVG inline в index.html, состояния через `data-state` на #avatar-stage

**Тестировать через:** `cd /root/wife-english-tutor && /root/voice-tutor/.venv/bin/python -m bot.cli "your sentence"` (используем voice-tutor venv, anthropic 0.97.0).

**Контракт LLM-ответа:** EN body + optional last line `Note: ... ` (RU explanation). `bot.llm.split_reply()` парсит обратно в (english, correction). Категории: articles, tenses, prepositions, word_order, vocabulary, pronunciation, plural_singular, agreement, other.