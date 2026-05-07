---
name: voice-tutor "слушает не отвечает" = OAuth 401 (mtime-check fix 2026-05-07)
description: Когда voice-tutor / @AISmartFriendBot ловит 401 invalid x-api-key — теперь автофикс через mtime watcher; диагностика и исторические причины
type: feedback
originSessionId: b344770e-99ab-467a-ba29-794f89607b88
---
Симптом: Mini App `voice.constantwrestling.cloud` или `@AISmartFriendBot` ловит `401 invalid x-api-key`, отвечает 503 (Mini App) или текстом ошибки (TG).

**Why:** Две независимые причины:
1. **Истекший токен.** OAuth-токен в `/root/.claude/.credentials.json` (общий с CELPIP и `claude` CLI) живёт ~8 часов. Просрочился — refresh не сработал.
2. **Stale in-process cache.** TG-бот и web-сервис — два процесса. Когда `claude` CLI или второй процесс рефрешит токен (single-use refresh_token consumed), первый продолжает шлёт старый из своего `_token_cache` → 401, хотя файл свежий. Симптом: `jq expiresAt` показывает много часов вперёд, но 401 всё равно прилетает. До 2026-05-07 force_refresh не помогал — refresh_token уже использован.

**How to apply:**
1. `jq '.claudeAiOauth | {expiresAt, mins:((.expiresAt - (now*1000))/60000|floor)}' /root/.claude/.credentials.json`
   - mins ≤ 0 → причина #1: истёк. Перезапуск или re-login через `claude` CLI.
   - mins > 60, но 401 → причина #2: stale cache.
2. `tail /root/voice-tutor/logs/{tutor,web-systemd}.log | grep -i "401\|invalid x-api-key"` — подтверждение.
3. **Прямой smoke-test токена:**
   ```bash
   TOKEN=$(jq -r '.claudeAiOauth.accessToken' /root/.claude/.credentials.json)
   curl -s -o /dev/null -w "%{http_code}\n" -X POST https://api.anthropic.com/v1/messages \
     -H "x-api-key: $TOKEN" -H "anthropic-version: 2023-06-01" \
     -H "anthropic-beta: oauth-2025-04-20" -H "content-type: application/json" \
     -d '{"model":"claude-haiku-4-5-20251001","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
   ```
   200 → токен валидный (тогда проблема в cache); 401 → токен мёртв (re-login через `claude` CLI).

**Фикс 2026-05-07 — mtime watcher в `bot/llm.py:get_anthropic_key`:**
- `_token_cache` хранит `file_mtime`. Перед использованием кеша — проверка `os.path.getmtime(CREDENTIALS_FILE)`.
- Если файл изменился извне (другой процесс обновил токен) → кеш считается stale → перечитываем credentials.json.
- Лог-маркер: `credentials.json updated by external process — picked up fresh token from disk`.
- В сочетании с `force_refresh` auto-recovery (фикс 2026-05-02) — теперь stale cache самовосстанавливается без рестарта, **если** refresh_token в credentials.json свежий.

**Когда фикс НЕ спасёт:**
- Refresh_token revoked глобально (deauth, смена пароля, длинная неактивность). Тогда `_refresh_oauth_token` вернёт не-200 → нужен интерактивный `claude /login` от Артёма.
- Бот рестартанулся сразу до того как `claude` CLI подхватил новый токен. Race на запись файла — теоретическая, маловероятная.

**Связанный антипаттерн:** другой агент / @DexClaudCodAIBot может попытаться "починить" запуском orphan-uvicorn на 0.0.0.0:8003 в обход systemd — порт занят, systemd не стартует, проблема усугубляется. Перед `systemctl start` всегда `ss -tlnp | grep 8003`.
