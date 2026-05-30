---
name: feedback-tutor-oauth-auth-token
description: "Туторы (wife/son/voice) шлют Claude через OAuth-токен из /root/.claude/.credentials.json — клиент ОБЯЗАН использовать auth_token=, не api_key=, иначе 401 invalid x-api-key. Форки дрейфуют."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d315614a-754b-4dd6-9d24-0c47b9b621f8
---

`bot/claude_client.py` во всех трёх форк-туторах (wife-english-tutor, son-french-tutor, voice-tutor) аутентифицируется в Claude **OAuth-токеном** (`claudeAiOauth.accessToken` из `/root/.claude/.credentials.json`, beta-header `oauth-2025-04-20`).

**Ловушка:** `anthropic.Anthropic(auth_token=key, ...)` шлёт `Authorization: Bearer` — правильно. `api_key=key` шлёт `x-api-key` → Anthropic возвращает **401 invalid x-api-key даже на свежий валидный OAuth-токен**.

2026-05-29: son-french-tutor молча не отвечал ("учитель не разговаривает") неделями — у него в `_client()` стоял `api_key=`, тогда как wife уже был пофикшен на `auth_token=`. Симптом каскада: 401 → пустой reply_len=0 → пустой TTS input → OpenAI 400 string_too_short → 503 на /api/voice. Рестарт НЕ помогает (баг в коде, не в токене); фикс — поменять на `auth_token=`.

**Урок:** форки дрейфуют. Если один тутор работает, а другой нет — `diff bot/claude_client.py` между ними ПЕРВЫМ делом. См. [[feedback-wet-corrector-sonnet]], [[feedback-tts-pc1-mandarin]].

**Сопутствующее (та же сессия):** PC1 Kokoro TTS (`100.99.211.123:8002`) хронически таймаутит (APITimeoutError каждый ход, ~8с простоя ×2 на ответ) → это была причина "жена: говорит с 3 раза, тормозит". Фикс: убрать `WET_TTS_BASE_URL` из wife `.env` → всегда OpenAI tts-1. Ollama (`:11434`) тоже мёртв. Для туторов cloud OpenAI TTS/STT надёжнее локального PC1.
