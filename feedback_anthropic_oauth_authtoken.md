---
name: feedback-anthropic-oauth-authtoken
description: anthropic.Anthropic(api_key=...) шлёт x-api-key; OAuth работает ТОЛЬКО через auth_token=. SDK 0.97.0+
metadata: 
  node_type: memory
  type: feedback
  originSessionId: eeb6bcbc-09a2-4e37-b01a-7f90d2807f2c
---

`anthropic.Anthropic(api_key=key)` — отправляет токен через заголовок
`x-api-key`, который работает только для обычных API keys из Console.

OAuth-токены `claudeAiOauth.accessToken` (из `/root/.claude/.credentials.json`)
работают **только** через `Authorization: Bearer ...`. Anthropic SDK 0.97+
имеет параметр `auth_token=`, который пишет именно этот заголовок.

**Симптом:** Anthropic API возвращает `401 invalid x-api-key` даже на
свежий токен, refresh API возвращает новый токен — он тоже отвергается.
В tutor-ботах это проявляется как "mini app слушает но не отвечает":
reply_len=0 → TTS получает пустую строку → 400 → 503 на stream endpoint.

**Why:** SDK по умолчанию интерпретирует `api_key` как простой API key и
выставляет `x-api-key`. До какого-то момента это могло работать
(возможно SDK раньше делал auto-detect), сейчас — нет.

**How to apply:** В любом tutor-боте или сервисе который использует
OAuth-токен Claude'а:
```python
anthropic.Anthropic(
    auth_token=key,                             # ← Bearer
    default_headers={"anthropic-beta": "oauth-2025-04-20"},
)
```
**не** `api_key=key`.

Sweep grep: `grep -rn "api_key=key" --include='*.py'` по всем
tutor-репам — если найдётся в Anthropic-конструкторе, чинить.

**Связано:** [[feedback_voice_tutor_oauth_500]] · [[feedback_oauth_force_refresh]] · [[feedback_tutor_tts_wiring]]
