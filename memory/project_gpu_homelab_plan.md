---
name: GPU homelab plan — 2x RTX 3090 на двух Windows ПК дома (PC1 ACTIVE 2026-05-07)
description: ПК1 настроен: Tailscale 100.99.211.123 + OpenSSH (root@vps→tkach@PC1) + Ollama as SYSTEM ScheduledTask; ПК2 ещё не подключен
type: project
originSessionId: ba8718ff-04fd-4b45-b897-9e35cdddc20f
---
**Hardware Артёма:**
- 2 desktop ПК **Windows** с RTX 3090 (24 GB VRAM каждая, 48 GB total)
- Стоят **дома**, дети 10-12 лет играют 3-5 часов **вечером** → 16 часов в сутки GPU свободны
- VPS — текущий 4BotsBybit-Trading + voice-tutor + ontime + всё прочее

**Use cases (от наибольшей экономии к меньшей):**
1. **voice-tutor / CELPIP-боты → local Whisper + XTTS + Qwen 2.5 32B** — экономия ~$60-100/мес OpenAI/Claude API + клонирование голоса Артёма
2. **emails-optimization → local Qwen** — экономия ~$20/мес
3. **GA optimizer → CuPy + parallel evaluation на GPU** — текущий 18ч прогон → ~30 мин
4. **OnTime invoice OCR → Donut/LayoutLMv3** — лучше Tesseract'a, бесплатно
5. **@solo_claude → SDXL/Flux картинки в едином стиле** — visual identity бесплатно
6. **Photo/video pipeline (то что мы 2026-05-07 делали 50 мин на CPU)** — секунды
7. **Trading research / fine-tune Llama на trading-логах** — для специализированного ассистента-аналитика

**Архитектура:**
```
Tailscale mesh (NAT-прозрачный, без проброса портов)
   ║         ║         ║
ПК1-Win   ПК2-Win    VPS-Linux
3090      3090       все боты
Ollama    ComfyUI    переключены на local API
+Whisper  +SadTalker
+XTTS     +Pinokio
```

**Roadmap — что делать (по очереди):**
1. **Tailscale на оба ПК + VPS** (10 мин). Бесплатный аккаунт, до 100 устройств. После этого VPS видит ПК1 по `winpc1.tailnet.ts.net`.
2. **ПК1 — Ollama for Windows** (30 мин). Скачать .exe, поставить, выставить env `OLLAMA_HOST=0.0.0.0:11434`, рестарт. `ollama pull qwen2.5:32b-instruct-q4_K_M`, `llama3.3:70b-instruct-q4_K_S`, `qwen2.5-coder:32b`.
3. **Voice-tutor → local LLM** (1 строка кода). `OpenAI(base_url="http://winpc1.tailnet:11434/v1")`. Сразу видно эффект, можно откатить.
4. **ПК2 — Stability Matrix** (https://lykos.ai) — установщик ComfyUI/A1111/Forge с моделями. SDXL Base+Refiner, Flux Schnell, GFPGAN.
5. **ПК2 — Pinokio** (https://pinokio.computer) — менеджер AI-приложений (SadTalker, Live Portrait, OpenVoice, AnimateDiff, EchoMimic — всё в один клик).
6. **faster-whisper-server в Docker Desktop на ПК1** — OpenAI-compatible API.
7. **XTTS-v2 / OpenVoice** — local TTS, опционально клонирование голоса Артёма.

**Дети-friendly mode:**
- Ollama `OLLAMA_KEEP_ALIVE=5m` — модель уходит из VRAM через 5 мин простоя, освобождает GPU для игры.
- Heavy jobs (fine-tune, batch image gen) запланировать через Windows Task Scheduler 23:00–8:00 Calgary.
- Watchdog: если процесс игры (CSGO/Fortnite/etc) активен → пауза AI workloads. Опционально, если 5-min keepalive не хватит.

**Текущее состояние (2026-05-07 20:25 MDT):**
- ✅ Tailscale: VPS=`100.72.50.25` (vps-trading), ПК1=`100.99.211.123` (desktop-f836b96), tailnet=borysiukartem1990@gmail.com
- ✅ OpenSSH на ПК1: `ssh tkach@100.99.211.123` с VPS работает (ed25519 ключ root@vps в `C:\ProgramData\ssh\administrators_authorized_keys` — потому что tkach в Administrators group; и в `%USERPROFILE%\.ssh\authorized_keys`)
- ✅ Ollama 0.23.1: запущен как Windows Scheduled Task `OllamaServe` (SYSTEM, AtStartup, RestartCount=3); env vars set Machine-level: OLLAMA_HOST=0.0.0.0:11434, OLLAMA_KEEP_ALIVE=5m, OLLAMA_ORIGINS=*
- ✅ Firewall: правило `OllamaAPI` TCP 11434 inbound; SSH правило `sshd` TCP 22
- ✅ qwen2.5:14b pulled (9 GB) — но slow для voice (17s prefill при 6k chars system+24msg history)
- ✅ qwen2.5:7b pulled (4.7 GB) — **active для voice-tutor**, 1.6s hot inference, 10s cold
- ✅ qwen2.5:32b-instruct-q4_K_M (19.9 GB) — pulled 2026-05-07 21:00 MDT
- 🔄 qwen2.5-coder:32b-instruct-q4_K_M — qualifying download in bg
- ❌ llama3.3:70b — НЕ влезет в одну 3090 (q4 = 40 GB, vram = 24); ждём ПК2 для split

**voice-tutor wired (2026-05-07):**
- `bot/llm_local.py` — OpenAI-compatible client → `http://100.99.211.123:11434/v1`
- `bot/llm.py` `call_claude()` диспатчит на local если `VT_LLM_BACKEND=local` AND no tools; multimodal/tool вызовы сами падают в ValueError → откат на Claude OAuth
- env vars: `VT_LLM_BACKEND`, `VT_LOCAL_LLM_URL`, `VT_LOCAL_LLM_MODEL`, `VT_LOCAL_LLM_MAX_TOKENS=300`, `VT_LOCAL_LLM_NUM_CTX=8192`
- Откат: `VT_LLM_BACKEND=claude` + restart
- Memory extractor + summarizer (BG Haiku) остались на Claude — там скорость не важна

**Performance findings:**
- 14b q4 на 3090: ~85 tok/s gen, но prefill долгий (~100 tok/s) → 17s на realistic prompt
- 7b q4 на 3090: ~150 tok/s gen (re-bench 2026-05-08: 174 tok/s warm), prefill быстрый → 1.6s на тот же prompt
- num_ctx=2048 default НЕ хватает для voice-tutor system prompt (~1500 tokens) + history → ставим 8192
- max_tokens=800 wasteful для голоса (persona держит 2-6 предложений) → cap на 300

**32B context trap (2026-05-08):**
- Дефолт qwen2.5:32b-instruct-q4_K_M запускается с context_length=32768 → KV-cache раздувает model до 31 GB → влезает только 23 GB в VRAM, 8 GB CPU offload → **4.2 tok/s** (непригодно)
- Fix: создан тег **`qwen2.5:32b-ctx4k`** (PARAMETER num_ctx 4096) → 20.85 GB полностью в VRAM, **37-43 tok/s**, 100% GPU
- Для всех клиентов (voice-tutor, emails, etc) использовать `qwen2.5:32b-ctx4k`, НЕ `qwen2.5:32b-instruct-q4_K_M` напрямую — иначе словишь spillover
- Команда создания (повторить если ПК1 переустановят): `POST /api/create {"model":"qwen2.5:32b-ctx4k","from":"qwen2.5:32b-instruct-q4_K_M","parameters":{"num_ctx":4096}}`

**Network (2026-05-08):**
- Tailscale между VPS↔ПК1 идёт через DERP-relay (Seattle), `direct connection not established`, latency 220-630ms
- Для Ollama терпимо (gen tok/s важнее), для voice-tutor real-time может ощущаться задержкой первого токена
- Чтобы пробить direct: на роутере дома открыть UDP 41641 или включить UPnP/NAT-PMP. Проверить тип NAT через `tailscale netcheck` на ПК1. Если CGNAT — port-forward не поможет.

**Models dir когда Ollama от SYSTEM:** `C:\Windows\System32\config\systemprofile\.ollama\models\blobs`

**Что осталось:**
1. Закончить pulls (32b, coder)
2. voice-tutor: `OpenAI(base_url="http://100.99.211.123:11434/v1", api_key="ollama")` — менять в коде voice-tutor, тест через TG-бот
3. ПК2 — Tailscale + установка (Stability Matrix / ComfyUI вместо Ollama; для image gen)
4. faster-whisper-server в Docker на ПК1 (для voice-tutor STT)
5. XTTS-v2 / OpenVoice на одной из машин (для TTS)

**Quirks обнаруженные:**
- PowerShell терминал на пасте длинной строки делал перенос → `Add-Content` записывал ключ на 2 строки. Workaround: разбивать длинные строки через `+` склейку или через scp + `-File` запуск .ps1 скрипта.
- `start /B ollama pull` через одноразовый SSH не выживает (process group killed). Лучше: API call POST /api/pull, или `schtasks` для async, или Run-Once Scheduled Task.
