---
name: son-french-tutor-andrii
description: "TG-бот для Andrii (~11-14yo) учит французский A1-A2. Persona Sophie (нова voice), avatar talking_loop.mp4, streaming TTS pipeline 2-3s latency. Bot id 8341136914."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0d922c64-3f45-4394-b337-23a2551a6ef1
---

Репо: `/root/son-french-tutor/` (forked from `/root/wife-english-tutor/` 2026-05-11). GH: `InfinitySudo/son-french-tutor` private, branch `main`, initial push 2026-05-11.

**Кто:** Andrii (TG id `5378761450`), сын Артёма, 11-14 лет, цель — французский A1-A2. Allowed = Artem + Liliia + Andrii.

**Стек:**
- Bot: id `8341136914`. На 2026-05-11 21:00 MDT: username `@FrenchTuporBot` (опечатка в URL), display name `@FrenchTutorBot`. Артём пытался переименовать через `/setname` — поменялся только display. Чтобы поменять @handle нужен `/setusername`. Код использует только токен, поэтому переименование не ломает ничего.
- Persona: **Sophie**, парижанка-учительница (TTS voice `nova` — env `WET_TTS_VOICE=nova`); раньше был Lucas/onyx, поменяно 2026-05-12
- Промпты в `bot/llm.py` — на французском, многоэлементные [FIX]'ы (один на каждое ошибочное предложение), русский input всегда обрабатывается
- LLM model: **Haiku 4.5** (`reply_for_turn` default переключен 2026-05-12). max_tokens=700.
- Latency pipeline: см. [[project_tutor_latency_pipeline]] — streaming TTS, STT race, sentence split, bg cat/vocab. Backend turn ~2-4s.
- Avatar: `web/static/avatar/idle.jpg` (photo, ~80% face crop) + `talking_loop.mp4` (28-46s SadTalker v1.4 + GFPGAN loop, см. [[project_sophie_lipsync]]). Stage square 360×360 в `style.css`. SadTalker per-reply lipsync **отключён** (`WET_LIPSYNC_URL` закомментирован) — слишком медленно.
- Default level `A1`, переключается через `/level A2|B1|B2`
- DB: SQLite `/root/son-french-tutor/data/tutor.db`
- Port: web 8766 (vs wife 8765, voice-tutor 8003)
- Env: `/root/son-french-tutor/.env` — `WET_` prefix сохранён ради минимума diff'а; OPENAI_API_KEY общий с wife
- PC1 STT: используется (Whisper auto-detect lang)
- PC1 TTS (Kokoro): **намеренно отключён** — English-only, не годится для FR; всегда OpenAI TTS
- PC1 LLM (Ollama qwen2.5:7b): word lookups, понимает FR

**Сервисы:**
- `son-french-tutor.service` — TG polling bot
- `son-french-tutor-web.service` — FastAPI на 127.0.0.1:8766 (Mini App)
- `son-french-tutor-digest.service` + timer — end-of-day digest
- `son-french-tutor-reminder.service` + timer — daily nudge

**Mini App (LIVE с 2026-05-11):**
- DNS A-запись `son.constantwrestling.cloud → 187.77.148.44` добавлена 2026-05-11 (TTL=600, Артём добавил вручную у регистратора)
- HTTPS cert: Let's Encrypt, expires 2026-08-10, auto-renew
- nginx vhost `/etc/nginx/sites-enabled/son-french-tutor` (443 → 127.0.0.1:8766, 80→443 redirect)
- URLs: `https://son.constantwrestling.cloud` (WebApp root) и `/read` (reader sub-app)
- Внимание: локальный systemd-resolved на VPS закэшировал NXDOMAIN до пропагации — `resolvectl flush-caches` не помогает, но это не блокирует cerbot/users (резолвят из публичных DNS)

**Menu button "🇫🇷 Open Tutor":** persistent ≡ кнопка в чате → `WET_WEBAPP_URL=https://son.constantwrestling.cloud`. Ставится через `set_chat_menu_button(MenuButtonWebApp(...))` в `_post_init` (см. `bot/tutor_bot.py`). Образец взят из `voice-tutor/bot/tutor_bot.py:715`.

**Books:** seed в `scripts/seed_books.py` — 12 французских адаптаций (Petit Prince, Boucle d'or, Chaperon Rouge, Trois Petits Cochons, Cendrillon, Belle au bois dormant, Alice, Pinocchio, Tour du monde en 80 jours, Trois Mousquetaires, 20000 Lieues, Fables La Fontaine). Seed работает через `call_claude` → 429 sonnet → haiku fallback.

**Якоря:** [[project_wife_english_tutor]] (не существует — wife живёт в [[feedback_voice_tutor_oauth_500]]), [[project_voice_tutor]], [[user_artem]]
