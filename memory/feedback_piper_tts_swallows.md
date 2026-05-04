---
name: Piper TTS Swallows Endings
description: Piper TTS глотает финальные согласные на коротких фразах; всегда добавляй apad pad_dur=1.0+ к выходу.
type: feedback
originSessionId: 27d1f047-ee71-403c-890c-181c769d7af9
---
Piper TTS (en_US-ryan-high и аналогичные модели) обрезает финальные согласные/гласные на коротких фразах ("now", "app", "out"). Слушатель слышит "Open it no..." вместо "Open it now."

**Why:** voice-coding модель не моделирует release-фазу последнего фонема, аудио стопает почти сразу после vowel onset. На длинных фразах не критично (последнее слово амортизируется паузой), на коротких CTA — заметно.

**How to apply:**
1. Всегда оборачивай piper output в ffmpeg apad:
   ```bash
   .venv/bin/piper --model X --output_file /tmp/raw.wav <<< "text"
   ffmpeg -i /tmp/raw.wav -af "apad=pad_dur=1.0" final.wav
   ```
2. Для коротких CTA-фраз добавляй "comma + extra word" чтобы дать estuary паузу:
   - Плохо: "Open it now."
   - Хорошо: "Open it now, and enjoy the app."
3. Целевая длительность video clip должна быть >= audio + 1.5s (в `record_overlays.py` уже учтено как `audio_duration + 1.5`).

Проверено на OnTime marketing video (2026-05-04): без apad "now" обрывается, с apad=1.0 + перефразировкой проблема исчезает.
