---
name: tutor-latency-pipeline
description: "4-фазная оптимизация /api/voice в tutor ботах (son/wife): Haiku + asyncio.gather + sentence split + LLM streaming + STT race + TTS streaming endpoint. 8s → 2-4s."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Контекст:** son-french-tutor и wife-english-tutor имеют один pipeline `/api/voice`: STT → LLM → TTS → return JSON с base64 mp3. Изначально 6-10с до первого звука у пользователя. К 2026-05-12 ужали до **~2-4с** через 4 phase.

**Why:** Артём заметил что сын засыпает между turn'ами урока, жена жаловалась на медлительность. Скорость важнее качества для daily-use tutor.

**How to apply:** при работе с новыми voice-pipeline ботами — копировать **тот же набор приёмов**. Конкретные диффы лежат в son-french-tutor commits `ee9ac73 → 7fa4a7c → 74d87bd → 16c73cb`, в wife-english-tutor `d9213e4`.

### Phase 1: Haiku + asyncio.gather (~2-3с win)
- `reply_for_turn` default model: Sonnet → **Haiku 4.5** (`claude-haiku-4-5-20251001`). First-token ~3× быстрее, для A1-A2 reply качество достаточное.
- TTS и `categorise_correction` (отдельный Haiku call) — через `asyncio.gather`, не sequential.
- `vocab.add_words` — fire-and-forget background task.

### Phase 2: Sentence-level TTS split (~1-1.5с win)
- `_split_first_sentence(text, min=25, max=70)` — берёт первое предложение (или comma split, fallback hard word break на 70+ chars).
- TTS первой фразы synchronous (~600ms), TTS остатка — `asyncio.create_task` в фоне, stash в `_TTS_REST_CACHE[rest_id]`.
- Endpoint `GET /api/voice/rest/{job_id}` — long-poll 30s до готовности.
- Client `audio.onended` → fetch rest → chain-play.

### Phase 3: TTS proxy streaming (~1.5-2с win)
- Не возвращать MP3 в base64 — отдать клиенту **token**, открыть `GET /api/voice/stream/{token}`.
- Stream endpoint использует `openai.audio.speech.with_streaming_response.create(...).iter_bytes(chunk_size=4096)`, yields bytes в `StreamingResponse(media_type="audio/mpeg")`.
- Браузер играет с **~300-500ms после открытия** (не ждёт весь файл).
- Token — single-use, `_TTS_PENDING.pop()`. Никакой extra auth (short-lived).

### Phase 4: LLM streaming + STT race (~0.5-1.5с win + stability)
- `call_claude_stream` через `anthropic.messages.stream(...).text_stream`. `reply_for_turn_stream` yields chunks.
- В voice_turn: blocking task accumulates chunks, **flush первого TTS chunk через `loop.call_soon_threadsafe(first_ready_evt.set)` как только safe sentence boundary AND `[FIX]` count opens == closes** (не split mid-tag).
- `_TTS_PENDING[token]` stash сразу при first chunk — OpenAI начинает греться пока Haiku пишет остаток.
- JSON всё равно ждёт `full_done_evt` (нужен полный text для UI + correction для "Try again" кнопки).
- **STT race**: `asyncio.wait` параллельно OpenAI Whisper и PC1 faster-whisper (через Tailscale `WET_STT_BASE_URL`). Первый non-empty wins. Без race OpenAI Whisper spike'ит до 10-15s; race кэп ~3-4с (PC1 stable baseline).

### Gotchas
- **`loop.run_in_executor()` уже возвращает Future, не coroutine** — нельзя оборачивать в `asyncio.create_task()`. Падает с `TypeError: a coroutine was expected, got <Future pending>`. Передавай Future прямо в `asyncio.wait`.
- **Cancelled run_in_executor task НЕ останавливает blocking thread** — wav_path может быть удалён через `finally` пока второй thread всё ещё читает файл. Логи покажут `FileNotFoundError`. Лечится `try: ... except` в blocking funcs.
- **`OPENAI_BASE_URL` в shell env переопределяет OpenAI client base_url** — см. [[feedback_openai_base_url_shell_override]].
- **`asyncio.create_task` нельзя для blocking functions** — нужно `loop.run_in_executor(None, fn)`, потом await его.

### PK-priority race (added 2026-05-12)
- 3 participants: PK1 (100.99.211.123), PK2 (100.73.22.1), OpenAI cloud.
- env: `WET_STT_BASE_URL` = primary on-prem (PK1), `WET_STT_BASE_URL_2` = secondary on-prem (PK2), `WET_STT_PK_HEAD_START` = grace seconds (default 1.5).
- PK1+PK2 fire immediately; OpenAI joins **only after grace** if no PK answered. Artem prefers PKs to win when up, but slow/offline PK doesn't block the turn.
- Same pattern in son-french-tutor, wife-english-tutor, voice-tutor. voice-tutor uses `VT_STT_BASE_URL_2` and `VT_STT_PK_HEAD_START`.

### Метрики после всех фаз
- Backend turn: **~1.8с** короткий reply / **~3.5с** с correction
- + Stream open OpenAI: ~300-500ms
- Total до первого звука: **~2.2с / 4с**

Применимо к любому voice→TTS pipeline. Скопируй паттерн в новый бот — `/root/son-french-tutor/web/app.py:voice_turn` — авторитетный образец.
