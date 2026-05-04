---
name: voice-tutor (@AISmartFriendBot)
description: Telegram голосовой собеседник + Mini App с continuous voice mode (VAD/barge-in); /root/voice-tutor; 2 systemd units; voice.constantwrestling.cloud
type: project
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
**Что:** Двухинтерфейсный голосовой компаньон Артёма. Build started 2026-05-02.
- **TG-бот** `@AISmartFriendBot` — chat-mode (voice/text in → voice out), long-term memory.
- **Telegram Mini App** на `https://voice.constantwrestling.cloud` — continuous voice loop с VAD: один тап «Talk» и дальше hands-free, бот отвечает голосом, пользователь может перебить голосом (barge-in).

**Why:** Артём искал нишу в voice-AI для commute. Langua/Talkpal/Praktika — только языковые курсы; ChatGPT-CarPlay — только iOS 26.4+, без памяти. Дыра — голосовой собеседник с long-term memory + multi-language + general topics + true hands-free (TG bot voice messages не autoplay'ятся, нужен WebApp с браузерным audio).

**How to apply:**
- Repo: `https://github.com/InfinitySudo/voice-tutor` (private)
- Код: `/root/voice-tutor`
- Прод: 2 systemd units
  - `voice-tutor.service` → `bot/tutor_bot.py` (TG polling)
  - `voice-tutor-web.service` → `uvicorn web.app:app --port 8003` (FastAPI)
- nginx vhost: `/etc/nginx/sites-enabled/voice-tutor` → `voice.constantwrestling.cloud` (LE cert) → `127.0.0.1:8003`
- DB: SQLite `/root/voice-tutor/data/tutor.db` — общая для TG bot и WebApp (TG `initData` валидируется HMAC, user_id матчится)
- ENV: `/root/voice-tutor/.env` — `VT_BOT_TOKEN`, `VT_OWNER_ID=504609639`, `OPENAI_API_KEY` (общий с CELPIP), `VT_TTS_VOICE=nova`, `VT_PERSONA_GENDER=female`, `VT_WEBAPP_URL=https://voice.constantwrestling.cloud`

**Архитектура памяти (3 слоя, per-profile с 2026-05-02):**
1. Live window — последние 24 сообщения as-is
2. Long-term facts — Haiku в фоне каждые 8 ходов извлекает в `memories` table; идут в system prompt
3. Rolling summary — когда backlog > 40, oldest 20 → text-сводка (`profile_summary` table)

**Multi-speaker (2026-05-02):**
- `profiles(id, name, owner_tg_id, is_default, embedding BLOB, samples)` — каждый голос = 256-d float32 embedding от resemblyzer
- `messages`, `memories`, `profile_summary` keyed по `profile_id` — контексты полностью изолированы между членами семьи
- Identification: на каждом /api/turn audio → ffmpeg 16kHz wav → resemblyzer → cosine vs enrolled profiles. Threshold 0.75 (env `VT_SPEAKER_THRESHOLD`)
- Если ни один профиль не enrolled — fallback на default profile владельца (legacy behaviour сохранён)
- При unknown speaker — отказ "Не узнаю голос. Зарегистрируй его в настройках профиля." (не пишем в чужой контекст)
- Endpoints: `GET/POST /api/profiles`, `POST /api/profiles/enroll` (multipart name+audio+optional profile_id), `DELETE /api/profiles/{id}`
- Legacy user_id-keyed функции в `bot/db.py` обёрнуты вокруг новых `*_p()` через `_default_profile_id(tg_id)` — TG bot не трогали
- Зависимости: `resemblyzer` + `torch` (CPU) → 1.5GB venv (~50MB модели + torch deps)

**Mini App ключевые фичи:**
- VAD: RMS-based, default 3000ms тишины, **adaptive 1.5×** после 2с речи (для длинных вопросов)
- MIN_SPEECH_MS=800 — короткие сегменты (шум) дискардятся, не отправляются
- Barge-in: пока бот говорит, mic параллельно слушает; threshold+5, sustained 250ms → playback pause → listen. Toggleable в settings.
- Live RMS-бар в settings для калибровки порога
- 350ms cooldown «твой ход» после ответа бота
- TG WebApp `initData` HMAC валидация → trust user_id

**Persona gender:** `nova` (женский голос) → `VT_PERSONA_GENDER=female` в env, GENDER_BLOCK в `bot/llm.py` принуждает женский род («я сказала»). Если менять voice → менять gender.

**UX-правила:**
- Voice-input в TG → voice-only reply (см. feedback_voice_chain_autoplay.md)
- `/memory` `/forget <id>` `/forget all` `/reset` — управление памятью
- `/voice` или menu-button «🎙 Live» открывают Mini App
