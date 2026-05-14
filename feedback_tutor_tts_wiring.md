---
name: tutor-tts-wiring
description: Tutor-bot TTS/STT must route to PC1 (Kokoro :8002 / Whisper :8001) with PC2 + OpenAI fallback; never let it silently fall back to OpenAI without a log
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 684f23a1-5fd6-499b-a3a9-251bef4fdb6b
---

В `wife-english-tutor` (и аналогичных tutor-ботах: `son-french-tutor`, `voice-tutor`) TTS и STT должны идти через ПК1 Kokoro/Whisper по `WET_TTS_BASE_URL` / `WET_STT_BASE_URL`. OpenAI — только последний fallback.

**Why:** Артём специально подключил [[project_pc1_homelab_active]] и ПК2 ради этих ботов. Раньше код использовал глобальный `openai = OpenAI(api_key=...)` без `base_url=`, и TTS тихо шёл на OpenAI — голос продолжал работать, но платный, а при отвале OpenAI бот «не разговаривал». Артём заметил это, когда `EnglishTecherTutorBot` 2026-05-14 писал текстом но не отвечал voice. Также см. [[feedback_openai_base_url_shell]] — `OPENAI_BASE_URL` через env легко роутит куда не надо.

**How to apply:**
- При любой работе с `_synthesize` / `_transcribe` в tutor-ботах: проверяй, что используется отдельный `OpenAI(base_url=…)` клиент, не глобальный `openai`.
- Сохраняй fallback chain: PC1 → PC2 → OpenAI, с `logger.warning` на каждый fallback (без него Артём не узнает, что ПК1 отвалился).
- При старте бота логируй `voice routing → TTS=…, STT=…`, чтобы регрессия была видна в логах.
- Если меняешь `.env` или `OpenAI` client — обязательно прогон smoke-test `_synthesize("hi", "/tmp/x.opus")` и проверь, что аудио > 0 байт.
