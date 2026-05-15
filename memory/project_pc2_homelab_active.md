---
name: pc2-homelab-active
description: "ПК2 (Art, RTX 3090 24GB) подключён 2026-05-12: Tailscale `borys@100.73.22.1`, SSH с ed25519 ключом, Ollama 11434 (qwen2.5:7b), faster-whisper 8001 (large-v3 CUDA), Tailscale firewall открыт. Hostname `Art`."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Доступ:**
- SSH: `ssh borys@100.73.22.1` — passwordless через VPS-ключ в `C:\ProgramData\ssh\administrators_authorized_keys`
- User: `borys` (admin); полное имя `art\borys`. Windows shell в SSH — cmd.exe по умолчанию, для PS используй `ssh ... powershell -NoProfile -Command "..."`
- Tailscale тот же аккаунт что и ПК1, mesh-доступ к всем

**Что крутится:**
- **Ollama** `:11434` — `qwen2.5:7b-instruct-q4_K_M` (4.68 GB). `OLLAMA_HOST=0.0.0.0:11434` Machine-scope env. Запуск через WMI `ollama serve` фоном (stdout → `C:\Users\borys\ollama.log`)
- **faster-whisper** `:8001` — `large-v3` на CUDA float16. FastAPI server `C:\Users\borys\whisper_server.py`, venv `C:\Users\borys\whisper_venv`. Auto-start через Scheduled Task **WhisperServer** (триггеры AtLogOn + AtStartup, restart on failure через 1 min, до 999 раз). Wrapper `C:\Users\borys\run_whisper.bat` ставит PATH к CUDA-wheels (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12` в venv site-packages) — БЕЗ этого ctranslate2 падает `cublas64_12.dll not found`. Лог `C:\Users\borys\whisper.log`. Управление: `Stop-ScheduledTask -TaskName WhisperServer` / `Start-ScheduledTask -TaskName WhisperServer`
- **CUDA**: driver 581.95, RTX 3090 24GB; cupy `not yet установлен`, sadtalker_venv нет (это PK1)

**Firewall:**
- Tailscale subnet `100.64.0.0/10` разрешён на портах 11434 и 8001. Если другой порт — `New-NetFirewallRule -DisplayName 'X' -LocalPort N -RemoteAddress 100.64.0.0/10 ...`

**Известные quirks (mirror PK1):**
- `Start-Process` от SSH умирает при disconnect — для долгих процессов используй `[wmiclass]'\\.\root\cimv2:Win32_Process'.Create(...)` с stdout-redirect в .log
- Non-ASCII символы (em-dash etc.) в скриптах ломают PowerShell parser — используй ASCII-only в .ps1 файлах
- Quote escaping через ssh+powershell+python ужас — заливай через scp .ps1/.py файлы, выполняй `powershell -ExecutionPolicy Bypass -File`

**Tutor-боты подключены к PK2 через STT race:**
- `WET_STT_BASE_URL_2=http://100.73.22.1:8001/v1` в son и wife `.env`
- `VT_STT_BASE_URL_2=http://100.73.22.1:8001/v1` в voice-tutor `.env`
- Race с PK-приоритетом (head-start 1.5s); cloud OpenAI joins после grace. Все три бота committed 2026-05-12.

**GA backtester (ready 2026-05-13):**
- `C:\Users\borys\ga_venv` — cupy-cuda12x 14.0.1, numpy, scipy, pandas, deap
- + NVIDIA runtime wheels: `nvidia-cuda-nvrtc-cu12`, `nvidia-cuda-runtime-cu12`, `nvidia-cublas-cu12`, `nvidia-curand-cu12`, `nvidia-cusolver-cu12`, `nvidia-cusparse-cu12` (нужны потому что CUDA Toolkit не stand-alone — driver сам не даёт `nvrtc.dll`)
- Все GA модули `C:\Users\borys\ga_gpu\*.py` (pipeline, signal_kernel, simulate_trade_kernel, kline_loader, backtest_cpu, ga_optimizer_gpu, pc1_run_wrapper, btc_sanity_check). Import smoke-test passed.
- klines cache **на PK2 нет** — для GA run пока нужно PK1 или scp cache. Кэш ~1.5GB.
- Warning `CUDA path could not be detected` cosmetic — cupy работает (verified arr.sum() on GPU device 0).

**Что НЕ установлено:**
- SadTalker / Wav2Lip / kokoro-tts — на PK2 нет, эти живут на PK1

**Когда нужно расширять:**
- Quick-Whisper test: `curl http://100.73.22.1:8001/` → `{"ok":true,"model":"large-v3","device":"cuda"}`
- Quick-Ollama test: `curl http://100.73.22.1:11434/api/tags`

Якоря: [[project_pc1_homelab_active]] (PK1 reference), [[feedback_pc1_ssh_quirks]] (применимо к обоим), [[project_tutor_latency_pipeline]] (где PK2 в pipeline)
