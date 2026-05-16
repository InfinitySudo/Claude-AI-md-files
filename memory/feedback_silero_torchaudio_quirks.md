---
name: silero-torchaudio-install-quirks
description: "Silero + torchaudio require two deps that are NOT pulled in by `pip install torch torchaudio` — install will silently succeed but runtime fails on first request"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f4c4861-fd60-4f57-b7af-c4260e03075c
---

При установке Silero TTS (через `torch.hub.load("snakers4/silero-models", "silero_tts")`) или любого pipeline, использующего `torchaudio.save()` с WAV/MP3 → ВСЕГДА доустанавливать вручную:

```
pip install soundfile      # torchaudio backend for save()
pip install omegaconf      # silero internal config loader
```

**Why:** 2026-05-15, install Kokoro+Silero на PC2 (`feedback_silero_torchaudio_quirks` originated). После `pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 + num2words fastapi uvicorn` запуск Silero падал с:
1. `ModuleNotFoundError: No module named 'omegaconf'` — внутри `torch.hub.load` для silero_tts; Silero authors hardcode `from omegaconf import OmegaConf` но не объявляют как dep.
2. `RuntimeError: Couldn't find appropriate backend to handle uri ... and format wav.` — `torchaudio.save()` с BytesIO+format='wav' требует `soundfile` package; torchaudio имеет dispatcher но без backend pip-package сам сэйв падает.

Оба silent в момент install — pip говорит OK, всё проваливается только на первом requestе. Wasted ~10 minutes отладки на PC2.

**How to apply:**
- Любой install Silero TTS, новых PCs или other tutors → add `soundfile` + `omegaconf` в **обязательном** order:
  ```
  pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
  pip install soundfile omegaconf num2words fastapi uvicorn pydantic
  ```
- При copy-paste setup с PC1 — PC1 уже имеет эти deps в venv, но они НЕ в основных install scripts/требованиях. Проверь `pip list | grep -iE "soundfile|omegaconf"` перед запуском.
- Если pipeline использует `torchaudio.save(BytesIO, ...)` или `torchaudio.load(BytesIO)` — нужен `soundfile`. `torchaudio.io.StreamReader` not enough.

Связанное: [[project_pc2_homelab_active]] (PC2 has both installed now), [[project_voice_tutor]] (использует Silero RU TTS).
