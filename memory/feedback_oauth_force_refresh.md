---
name: oauth-force-refresh
description: "When Claude returns 401, the 401-handler must call refresh API even if disk expiresAt is in the future — Anthropic revokes tokens before formal expiry under parallel usage"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 684f23a1-5fd6-499b-a3a9-251bef4fdb6b
---

`get_anthropic_key()` принимает `force_refresh=True` от 401-обработчика. Эта ветка ДОЛЖНА реально вызвать `_refresh_oauth_token()` через `https://platform.claude.com/v1/oauth/token`, даже если на диске `expiresAt` ещё в будущем. Anthropic отзывает access_token досрочно при параллельном использовании refresh_token (несколько ботов на одном `~/.claude/.credentials.json`).

**Why:** Артём 2026-05-14 поймал @EnglishTecherTutorBot в "молчит" режиме — web.log показывал `LLM stream error: 401 invalid x-api-key`, при этом `expiresAt` в credentials.json был `+3h` от now. Старый код имел ветку:
```python
if disk_token_fresh and (not force_refresh or cache_stale): return access_token
```
которая возвращала уже отозванный токен — refresh API никогда не вызывался. См. [[feedback_voice_tutor_oauth_500]] (как симптом) и [[feedback_oauth_rate_limits]] (паралельные процессы жгут токены).

**How to apply:**
- Условие выхода с диска должно быть **только** `if disk_token_fresh and not force_refresh:` — force_refresh всегда обязан хитнуть refresh API, не уважая disk.
- 401-обработчик в `call_claude` / `call_claude_stream` / `_safe_create` обязан передавать `force_refresh=True` при retry, не только сбрасывать `_token_cache['file_mtime']=0`. Сброс mtime ничего не даёт, потому что disk_token_fresh выигрывает.
- Чинить во ВСЕХ местах где есть свой `get_anthropic_key` (wife-english-tutor, son-french-tutor, voice-tutor, и любых будущих tutor-проектах). Все три файла идентичны — лучше всего консолидировать в shared `claude_oauth` модуль.
