---
name: PC1 Homelab — ACTIVE inventory
description: Что доступно на ПК1 Артёма (RTX 3090, Tailscale 100.99.211.123) для тяжёлых задач — SSH, Ollama, faster-whisper, autostart
type: project
originSessionId: 8d2f9d7c-3290-489b-addf-b57a4e9806fa
---
**Use this whenever heavy compute is needed** — VPS остаётся для live-сервисов; всё что занимает много времени (LLM inference, транскрипция, рендеринг видео, photo restoration, бэктесты, ML training, batch image-gen) гонять через ПК1.

## SSH доступ с VPS
```
ssh tkach@100.99.211.123
```
- Public-key auth, ключ VPS (`/root/.ssh/id_ed25519.pub`) уже в `C:\ProgramData\ssh\administrators_authorized_keys` на ПК1 + в `%USERPROFILE%\.ssh\authorized_keys`. Работает без пароля.
- Платформа: Windows 11, Python 3.11.9 в `C:\Program Files\Python311\python.exe`. Docker НЕ установлен. Используй venv'ы под `C:\Users\tkach\<project>\venv`.
- ⚠ `Start-Process -WindowStyle Hidden` через ssh **убивает дочерние процессы при закрытии ssh**. Для длинноживущих сервисов используй `Register-ScheduledTask` с `-AtStartup` + RunLevel Highest + UserId SYSTEM (см. ниже).

## Доступные сервисы (auto-start at boot)

| Task | Endpoint | Что | Models |
|---|---|---|---|
| **OllamaServe** | `http://100.99.211.123:11434/v1` | LLM (OpenAI-compatible) | qwen2.5:7b/14b/32b, qwen2.5-coder:32b |
| **faster-whisper-server** | `http://100.99.211.123:8001` | STT (OpenAI `/v1/audio/transcriptions`) — также возвращает word-timings | large-v3 на CUDA float16 (с 2026-05-13, ранее small.en — переключили чтобы выровнять с PK2) |
| **kokoro-tts-server** | `http://100.99.211.123:8002` | TTS (OpenAI `/v1/audio/speech`) — голоса alloy/echo/fable/onyx/nova/shimmer/coral/ash mapped → kokoro. **English only.** | Kokoro-82M-v1.0 на onnxruntime-gpu |
| **silero-tts-server** | `http://100.99.211.123:8005` | TTS (OpenAI `/v1/audio/speech`) — **Russian** with proper stress (Калгари → КА́лгари). voice mapping nova→kseniya и т.д. | silero v4_ru на torch+CUDA |

## Hardware
- **GPU**: NVIDIA RTX 3090, 24576 MiB VRAM (~23.3 GiB free idle)
- **Disks**: C: 1 TB OS (~580 GB free), **D: 2 TB DATA (~1.76 TB free)** — для klines/datasets/heavy artifacts
- **Python**: 3.11.9 в `C:\Program Files\Python311\python.exe`. Tailscale active, hostname `desktop-f836b96`.

## GA Optimizer (RTX 3090) — ACTIVE
- **PC1 dir**: `C:\Users\tkach\ga_gpu\` (всё там — код, klines cache, results)
  - `ga_optimizer_gpu.py` — GPU-vectorized GA (~70× быстрее CPU)
  - `pc1_run_wrapper.py` — обёртка с per-PID logs (Defender lock issue) + ga_run.current pointer file
  - `kline_loader.py`, `backtest_cpu.py`, `pipeline.py` — engine
  - `run_ga.ps1` — PowerShell launcher
  - `klines/` — 5m + D кэш Binance/Bybit
  - `dashboard_symbols.txt` / `full_symbols.txt` — universe options
  - `ga_gpu_results.json` — последний результат
  - `ga_run_<PID>.log` / `.err` — per-run stdout/stderr
- **VPS endpoint**: `POST /api/ga/run` с `{"target":"pc1"}` (с 2026-05-10 — default везде: HTML radio checked + index_v2 + weekly trigger)
- **Status sync**: `pc1_status_poller.py` запускается на VPS как `ga-pc1-poller-<ts>.service`, забирает `ga_run.current` и pid log с PC1, пишет в `data/ga_status.json`. Dashboard читает оттуда.
- **ETA**: ~15-20 минут на 276 symbols × 30 gen × 40 pop (vs ~31 часа на VPS CPU)
- **Запуск из CLI**:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/ga/run \
    -H 'Content-Type: application/json' \
    -d '{"target":"pc1","pop":40,"gens":30}'
  ```
- **Где смотреть live**:
  - PC1 stdout: `ssh tkach@100.99.211.123 'type C:\Users\tkach\ga_gpu\ga_run_<PID>.log'`
  - GPU: `ssh tkach@100.99.211.123 'nvidia-smi'`
  - VPS: `cat /root/4BotsBybit-Trading/data/ga_status.json` (синхронизируется поллером)

Все **persistent** через `Register-ScheduledTask -AtStartup -Principal SYSTEM`. На boot стартуют, при крэше перезапускаются (RestartCount=5).

## Где живёт faster-whisper-server
- Код: `C:\Users\tkach\fws\serve.py` (~80 строк, FastAPI обёртка)
- venv: `C:\Users\tkach\fws\venv`
- Зависимости: `faster-whisper`, `fastapi`, `uvicorn[standard]`, `python-multipart`, `nvidia-cublas-cu12`, `nvidia-cudnn-cu12`
- ⚠ **Критично**: scheduled task action оборачивает в `cmd /c "set PATH=...nvidia\cublas\bin;...nvidia\cudnn\bin;%PATH% && python ..."`. Без этого `cublas64_12.dll` не найдена.
- Машинная env `FWS_MODEL=large-v3` (с 2026-05-13). `WHISPER_MODEL=*` machine vars в serve.py НЕ читаются — там `FWS_MODEL/FWS_DEVICE/FWS_COMPUTE_TYPE`, не WHISPER_*.
- Логи: `C:\Users\tkach\fws\stdout.log`, `stderr.log`
- Re-register скрипт: `C:\Users\tkach\fws\register_fws_task.ps1`

## Где живёт silero-tts-server (Russian TTS)
- Код: `C:\Users\tkach\silero-tts\main.py` (FastAPI OpenAI-compatible)
- venv: `C:\Users\tkach\silero-tts\venv` (torch+CUDA 12.1, torchaudio, omegaconf, fastapi, num2words, soundfile)
- Модель: `snakers4/silero-models` v4_ru, скачивается в `C:\WINDOWS\system32\config\systemprofile\.cache\torch\hub` при первом запуске SYSTEM-task
- start.bat env (важно — оба нужны):
  - `set SILERO_DEFAULT_VOICE=baya` — текущий выбранный голос Артёма (2026-05-14). Сменить голос = только этот var + перерестарт scheduled task.
  - `set PATH=C:\Users\tkach\AppData\Local\Microsoft\WinGet\Links;%PATH%` — без этого SYSTEM task не находит ffmpeg.
- Voice mapping: alloy→baya, echo/fable→eugene, onyx→aidar, shimmer→xenia, **nova→DEFAULT_SPEAKER** (т.е. на что бы ни переключили env — клиент шлёт voice="nova" и получит правильный). Доступные: aidar, baya, kseniya, xenia, eugene.
- Sample rate 48 kHz, put_accent=True/put_yo=True для корректной просодии
- ⚠ **Цифры**: Silero v4_ru глотает голые digits ("109543" → молчит/обрывает). Поэтому в server.py есть `_expand_numbers()` через `num2words(lang="ru")` ДО синтеза — `109543` → «сто девять тысяч пятьсот сорок три», `$100` → «сто долларов», `25%` → «двадцать пять процентов», `2.5` → «два целых пять». Без этого preprocessing любые числа в TTS-выводе будут пропадать.
- Smoke-test: `curl -X POST http://100.99.211.123:8005/v1/audio/speech -d '{"voice":"nova","input":"Биткоин 109543","response_format":"mp3"}'`
- Логи (наш custom format с текстом запроса) в `C:\Users\tkach\silero-tts\stderr.log` (uvicorn перенаправляет logging.StreamHandler в stderr).
- ⚠ `taskkill /im python.exe` или `/fi "MEMUSAGE gt 500000"` **прибивает все TTS-сервисы сразу** (kokoro+silero оба занимают 800MB+). Всегда таргетить по PID через `wmic ... where "commandline like '%main.py%'"` (не "silero" — путь main.py относительный, не матчится) или останавливать через schtasks.

## Где живёт kokoro-tts-server
- Код: `C:\Users\tkach\kts\serve.py`
- venv: `C:\Users\tkach\kts\venv`
- Зависимости: `kokoro-onnx`, `onnxruntime-gpu`, `soundfile`, `av` (для mp3 encode), `fastapi`, `uvicorn[standard]`, `huggingface_hub`
- Модели локально (не качаются с HF на каждый рестарт): `C:\Users\tkach\kts\models\kokoro-v1.0.onnx` (310MB) + `voices-v1.0.bin` (28MB)
- Источник моделей: `github.com/thewh1teagle/kokoro-onnx` releases (MIT, 2.5k stars), SHA256 model=7D5DF8EC...3636A6C5, voices=BCA610B8...9F1FBF7D — те же файлы что и `onnx-community/Kokoro-82M-v1.0-ONNX` на HF, просто voices в combined формате.
- Voice mapping в коде: OpenAI shimmer/nova/fable/etc → af_heart/af_bella/bf_emma/etc.
- Тот же CUDA-PATH wrapper что у faster-whisper.
- Re-register скрипт: `C:\Users\tkach\kts\register_kts_task.ps1`

## Подключение клиентов на VPS
```python
# STT
client = OpenAI(base_url="http://100.99.211.123:8001/v1", api_key="dummy", timeout=15)

# LLM
client = OpenAI(base_url="http://100.99.211.123:11434/v1", api_key="ollama", timeout=60)
```

## Бенчмарки
- Whisper small.en на 56-секундное аудио (~150 слов главы) с word_timestamps: ~12 сек, RTX 3090 не прогревалась.
- Cold start (load model + cuDNN warmup): ~8 сек на первый request, потом 2-3× быстрее.

## Когда использовать
**На ПК1:**
- LLM-генерация контента (переводы, главы книг, словарные карточки) — qwen2.5:7b быстрее и бесплатнее Claude Haiku
- Whisper транскрипция (с word timings для karaoke и т.п.)
- Photo restoration (GFPGAN, LaMa, DeOldify, SadTalker — отдельный venv)
- ML training (GA optimizer, meta-labeler retrains)
- Batch обработка чего угодно (PDF→текст, видео-рендер ffmpeg)

**На VPS:**
- Live-сервисы (Telegram polling, FastAPI/nginx, cron-таски)
- Stateful данные, БД, persist-storage
- Любые fallback'и для ПК (если PC выключен)

## Pattern: ПК1 как primary, VPS-OpenAI как fallback
```python
try:
    result = local_call(timeout=8)  # PC1
except Exception:
    result = openai_call()  # fallback
```
Всегда жёсткий timeout — если PC1 выключен, не висим.
