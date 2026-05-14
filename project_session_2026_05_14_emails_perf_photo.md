---
name: session-2026-05-14-emails-perf-photo
description: "Checkpoint сессии 2026-05-13/14 — perf-overhaul emails-bot, Calendar OAuth, photo-restoration на PK1 GPU, tim_proposal, фикс tutor-ботов"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b14e18d-63a6-4d91-a38e-33d997ae386b
---

## Что сделано в сессии (закоммичено + pushed)

### emails-optimization (4 commits)
- **Calendar OAuth** — `app/calendar_client.py`: list_events / free_slots (9-18 Mon-Fri Edmonton) / create_event / move_event через googleapiclient. OAuth flow через http://localhost paste-back (urn:oob deprecated, нужен PKCE off, OAUTHLIB_INSECURE_TRANSPORT=1). credentials: `google_credentials.json`, token: `google_token.json` — оба в .gitignore.
- **Perf Tier 1+2+4**: prompt caching (PERSONA_BASE + REWRITE_SYSTEM + emit_proposal as cache breakpoint в PLANNER_TOOLS), streaming AI Plan (`safe_stream` + `_split_first_sentence` + `on_first_sentence` callback → "🤖 <intent>" в TG за ~1с), parallel tool calls (ThreadPoolExecutor 4 workers).
- **Tier 3 STT race** PK1+PK2+OpenAI head-start 1.5s в `_whisper_transcribe_race` (env: `EMAILS_STT_BASE_URL_1/2`, `EMAILS_STT_PK_HEAD_START`).
- **/demo + DRY-RUN** — `app/demo.py` cmd_demo / cmd_demo_end. demo email с labels='demo:1' → real planner flow, _execute_action блокирует send_email/create_event/move_event по labels. Artem'ов bot теперь даёт preview AI Plan без trашить Tim's queue.
- **Shadow LLM** — `app/ollama_race.py` + triage shadow в БД (новые колонки `triage_shadow_*`). poller env: `EMAILS_TRIAGE_SHADOW=1`, `EMAILS_TRIAGE_SHADOW_MODEL=qwen2.5:32b-instruct-q4_K_M`. CLI: `python3 -m app.triage --shadow-stats`.
- **docs/tim_proposal.md** + **PDF** — 3-tier pricing (Essentials $700 / **Standard $1,100** ★ / Premium $1,800 CAD/мес + setup $2,500/3,500/5,000). ROI: 200 emails/day × 1.5h × $75-100/h = $2.5-3.3k/мес.
- **docs/tim_user_guide.md** — освежён (Calendar real, /demo, 🤖 Agent button).
- **marketing/** — 14-scene presentation video (2:52, 11 MB), Piper TTS + Playwright + ffmpeg. Pipeline: `scenes.py` → `gen_audio.py` → `record.py` → `compose.sh`.

### voice-tutor
- TTS playback safety: 30s safety timer + streaming `new Audio(streamUrl)` восстановлен (fetch-blob fix ломал iOS), visible debug в statusEl, `audio.muted=false; volume=1` явно.
- turn_stream endpoint буферизует bytes и отдаёт **Response с Content-Length** (не StreamingResponse) — iOS Safari нужен Content-Length чтобы `ended` fires.
- Kokoro toggle через `_tts_clients()` helper — но **отключен** в .env (`VT_TTS_BASE_URL=` закомменчен): voice-tutor multilingual, Kokoro English-only → произносит cyrillic как китайский.

### wife-english-tutor
- **Kokoro TTS на PK1:8002 включён** в .env + `_tts_local` client + `_synthesize_blocking` fallback chain. Warm latency: ~0.93s (vs ~1.5-2s OpenAI), бесплатно. wife English-only — Kokoro корректно произносит.
- 30s safety timer + cache-bust + STT max_retries=0 timeout 8s.

### son-french-tutor
- 30s safety timer + cache-bust + STT max_retries=0.
- Kokoro **НЕ** включён (French → Kokoro English-only daje тарабарщину).

## Что работает / endpoints / Scheduled Tasks

**PK1 (DESKTOP-F836B96, tkach):**
- :8001 faster-whisper-server — `large-v3` (переключили с small.en через `FWS_MODEL`). Scheduled Task `faster-whisper-server`.
- :8002 kokoro-tts-server. Scheduled Task `kokoro-tts-server` (restart count 999, не 5 как было).
- :8004 PhotoServer (**NEW**) — `D:\photo\server.py` FastAPI. GFPGAN warm 0.2s + LaMa warm. DeOldify subprocess в `D:\photo\deoldify_venv` (`fastai 1.0.61` + torch 2.0.1+cu118) — реализован но в e2e тесте **FAILED_SKIPPED** — нужно дебажить субпроцесс (вероятно DeOldify path / model path / import error). Scheduled Task `PhotoServer`.
- :11434 Ollama — все модели (llava:13b + qwen 7b/14b/32b + qwen-coder 32b).

**PK2 (ART, borys):**
- :8001 faster-whisper large-v3. Scheduled Task `WhisperServer` (auto-restart 999×1min).
- :8002 — нет (Kokoro живёт только на PK1).
- :11434 Ollama — pull в процессе на момент завершения сессии. Готово: 7b, 14b, 32b. Качается: qwen-coder:32b 14% (~35 min ETA). После — llava:13b. Marker file `C:\Users\borys\.ollama_pull_done` — пока NOT exists. Scheduled Task `OllamaModelPull` (idempotent через marker, restart 99×2min, AtLogOn+AtStartup).

## Что осталось open (для завтра)

1. **PK2 Ollama pull** — wait for `.ollama_pull_done` marker. ETA ~50 min с момента 2026-05-14 02:50 local. Когда готово — shadow race реально пойдёт PK1+PK2 параллельно (сейчас PK1 always winning потому что 32b только на PK1).

2. **DeOldify subprocess FAILED_SKIPPED** — диагностить. Возможные причины: deoldify import path, model loading, env activation в subprocess. Тестовый кейс: `D:\photo\samples\Adele_bw.png` → POST `/restore?deoldify=true` → headers покажут какая stage сфейлилась. `D:\photo\deoldify_runner.py` запускается из `D:\photo\deoldify_venv`. Логи в `D:\photo\server.log`.

3. **Shadow stats на 32b** — после нескольких дней копится сравнение Claude Haiku vs qwen2.5:32b на triage. Если ≥90% triage_class + 100% business_id на 50+ rows → promote (flip default planner to Ollama, Claude становится fallback). Сейчас 14b давал 40% на triage_class — 32b ожидается лучше.

4. **Tim proposal** — отправлен Артёму в TG как .md + PDF через @AISmartFriendBot. Артём решает forward Тиму с какой подачей. Tier выбирает Tim → setup в работу.

5. **Phase 4 finalisation** — VPS-side клиент для PhotoServer (TG бот endpoint который принимает фото → POST на PK1 :8004 → возвращает restored). Пока сервер работает, клиента нет.

## Ключевые decisions сессии (для контекста на завтра)

- **Kokoro = English-only**. Не использовать для voice-tutor (multilingual) или son (French). OK для wife (English).
- **iOS Safari + chunked MP3 = stuck "ended"**. Решение: либо buffer + Content-Length (voice-tutor sees), либо 30s safety fallback (все три). Streaming new Audio(streamUrl) работает на 99% iOS, fetch-blob ломает.
- **Streaming AI Plan через `on_first_sentence` callback** — Anthropic SDK `messages.stream()` + `text_stream` + `loop.call_soon_threadsafe(set)` event. Хорошо работает в production, латентность first-message → ~1с.
- **Pricing для Тима**: Standard $1,100 CAD/мес recommended. Не давать "Friend" tier — anchors для следующих клиентов.
- **AI бизнес стратегия (обсудили)**: купить 2× RTX 5090 (~$16-20k CAD all-in) когда будут 5-10 paying customers. До того — bootstrap на 2× 3090 которые уже стоят. Cloud burst (Lambda Labs $1.50/h H100) для пиков.

Якоря: [[project_pc1_homelab_active]] [[project_pc2_homelab_active]] [[project_ollama_race_shadow]] [[project_photo_restoration]] [[project_emails_optimization]]
