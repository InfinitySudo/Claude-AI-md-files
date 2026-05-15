---
name: tutor-bots OAuth 401 (drop-cache fix 2026-05-12)
description: voice-tutor / wife-english-tutor / son-french-tutor ловят 401 invalid x-api-key из-за race с DexClaud за общий credentials.json — fix: drop-cache-and-reread (lifted from DexClaud), не force-refresh
type: feedback
originSessionId: b344770e-99ab-467a-ba29-794f89607b88
---
**Симптом:** PWA отдаёт "voice error 500", TG-бот — "Sorry, my brain glitched". В `logs/web.log`: `anthropic.AuthenticationError: 401 invalid x-api-key`. `jq expiresAt` показывает часов 8 вперёд, прямой curl с этим же токеном даёт 200 — то есть в файле токен валидный, в памяти процесса — нет.

**Why (root cause):**
`/root/.claude/.credentials.json` шарится между 5+ процессами: voice-tutor (2 сервиса), wife-english-tutor (2), son-french-tutor (2), claude-telegram-bot=@DexClaudCodAIBot, CELPIP-боты, сам `claude` CLI. **refresh_token у Anthropic OAuth single-use** — после одного refresh старый токен серверно invalidated. Каждый процесс держит in-memory cache токена. Когда A делает refresh → его cache живой, B/C/D с старым in-mem токеном получают 401, хотя credentials.json уже обновлён.

**Антипаттерн (не делать):** при 401 звать `get_anthropic_key(force_refresh=True)`. force_refresh идёт в refresh API call, который consumes refresh_token. Если credentials.json _уже_ свежий от другого процесса — refresh API даст 200, но реально вернёт инвалидированный токен (race). Логи: `calling refresh API → invalid x-api-key`.

**Фикс 2026-05-12 (lifted from @DexClaudCodAIBot):**
В `bot/claude_client.py` (wife + son) при 401:
1. `_token_cache["access_token"] = ""` и `_token_cache["file_mtime"] = 0.0` — обнуляем mem cache.
2. **Не зовём force_refresh.** Просто retry с фрешим `_client()`.
3. Следующий `get_anthropic_key()` через mtime watcher перечитает credentials.json и подхватит свежий токен, который положил туда другой процесс (обычно DexClaud).
4. Если на диске токен тоже мёртв → один раз попробуем refresh API.
5. До 2 retries; если не зашло — `raise`.

DexClaud делает то же самое (`claude_bot.py:948-952`): `_token_cache["access_token"] = ""` + return error → следующее сообщение работает.

**`claude auth login --yes` устарел в CLI 2.1.140 (--yes снят).** В DexClaud `_relogin_claude_cli()` живой rudiment, не работает. В tutor-боты НЕ переносить. Если refresh_token revoked глобально (раз в месяц, deauth, смена пароля) — нужен интерактивный `claude` re-login от Артёма; бот в этом случае напишет в лог `refresh API failed — token cannot be renewed`.

**Когда фикс НЕ спасёт:**
- refresh_token revoked глобально → ручной `claude` CLI re-login.
- Все 2 retry попали в race-окно (доли секунды) — теоретически возможно; третья попытка в следующем сообщении пользователя сработает.

**Диагностика:**
1. `jq '.claudeAiOauth | {expiresAt, mins:((.expiresAt - (now*1000))/60000|floor)}' /root/.claude/.credentials.json` — mins>60 + 401 = race с другим процессом (фикс работает); mins≤0 = ручной re-login.
2. `grep -E "invalid x-api|refresh API failed|dropping cache" /root/{wife-english-tutor,son-french-tutor,voice-tutor}/logs/web.log | tail`
3. Direct smoke-test токена: `TOKEN=$(jq -r '.claudeAiOauth.accessToken' /root/.claude/.credentials.json); curl -s -o /dev/null -w "%{http_code}\n" -X POST https://api.anthropic.com/v1/messages -H "x-api-key: $TOKEN" -H "anthropic-version: 2023-06-01" -H "anthropic-beta: oauth-2025-04-20" -H "content-type: application/json" -d '{"model":"claude-haiku-4-5-20251001","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'` → 200 валидно, проблема в кеше.

**voice-tutor `bot/llm.py` тоже на drop-cache** (commit `5366e97`, 2026-05-12, preventive). Особенность: `_safe_create(client_holder, ...)` принимает client как 1-эл список — на 401 mid-tool-loop client пере-создаётся, и tool-итерации продолжают работать с восстановленным клиентом без потери прогресса.

**Связанный антипаттерн:** другой агент пытается "починить" запуском orphan-uvicorn на 0.0.0.0:8003/8765/8766 в обход systemd — порт занят, проблема усугубляется. Перед `systemctl start` всегда `ss -tlnp | grep <port>`.
