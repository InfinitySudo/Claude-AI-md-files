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
- ⚠ **`openai_client` (cloud OpenAI) ОБЯЗАТЕЛЬНО создавать с `base_url="https://api.openai.com/v1"`** — иначе `OPENAI_BASE_URL=...deepseek...` из `.env` уведёт на DeepSeek и вернёт 404 на TTS endpoints. Раньше пряталось потому что для русского сначала шло в Silero и fallback не дёргался; в voice-tutor 2026-05-14 при переключении RU на cloud nova вылез 404. Касается `web/app.py` и `bot/tutor_bot.py` обоих.
- Сохраняй fallback chain: PC1 → PC2 → OpenAI, с `logger.warning` на каждый fallback (без него Артём не узнает, что ПК1 отвалился).
- При старте бота логируй `voice routing → TTS=…, STT=…`, чтобы регрессия была видна в логах.
- Если меняешь `.env` или `OpenAI` client — обязательно прогон smoke-test `_synthesize("hi", "/tmp/x.opus")` и проверь, что аудио > 0 байт. CLI smoke-test: `set -a; source .env; set +a` ПЕРЕД `python -c …`, иначе подхватится shell-`OPENAI_API_KEY` (не тот ключ, чужой `sk-5466e...` 401-ит).
- В voice-tutor с 2026-05-14 RU-text роутится в OpenAI nova (HD) по умолчанию (`VT_RU_TTS_BACKEND=openai`, `VT_OPENAI_TTS_MODEL=tts-1-hd`). Silero v4_ru остаётся доступен на ПК1:8005 как опция через `VT_RU_TTS_BACKEND=silero` — голос baya без акцента, но Артём предпочёл OpenAI nova за теплоту.
