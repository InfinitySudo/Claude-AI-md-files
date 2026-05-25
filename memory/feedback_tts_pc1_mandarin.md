---
name: tts-pc1-mandarin
description: "PC1:8002 TTS — НЕ настоящий OpenAI, локальная модель с китайско-английским уклоном на русском. Для product-видео всегда cloud OpenAI."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: eb2acf2d-6373-4894-a23c-0c81abe522d7
---

Локальный TTS на `http://100.99.211.123:8002/v1/audio/speech` экспонирует OpenAI-совместимый API с 8 voice'ами (`nova`, `onyx`, `shimmer`, …) — **но для русского текста выдаёт mandarin-звучащий бубнёж**. Whisper-1 на том же PC1 не смог транскрибировать тестовую русскую фразу — выдал «Продолжение следует…».

Та же фраза через `https://api.openai.com/v1/audio/speech` (cloud, `tts-1-hd` / `gpt-4o-mini-tts`, voice=`nova`) — чистый русский, Whisper транскрибировал точно.

**Why:** PC1:8002 — это вероятно Kokoro-TTS или OpenVoice со «спойлинговым» русским. Voice-tutor (@AISmartFriendBot) использует chain `PC1 → PC2 → OpenAI fallback` — то есть когда местная модель «прокатывает», голос тренируется на лету и звучит ok; для статичной генерации длинной речи fallback не срабатывает.

**How to apply:**
- Для всех **product-видео, демо-роликов, сейлз-материалов** — только cloud OpenAI напрямую, никаких PC1
- Для **tutor-ботов в реальном времени** — chain `PC1→PC2→OpenAI` оставить (он сам падает в cloud если что)
- Перед публикацией любого аудио — STT-проверка: если Whisper не разбирает русский, значит TTS говорит не по-русски
- Связано с [[feedback_tutor_tts_wiring]] (правило про fallback chain)
