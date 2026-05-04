---
name: voice-tutor "слушает не отвечает" = OAuth 401 (две причины: истечение ИЛИ stale cache)
description: Когда voice-tutor / @AISmartFriendBot ловит 401 invalid x-api-key — может быть истёкший токен ИЛИ stale in-process cache; чек обоих
type: feedback
originSessionId: b344770e-99ab-467a-ba29-794f89607b88
---
Симптом: Mini App `voice.constantwrestling.cloud` или `@AISmartFriendBot` ловит `401 invalid x-api-key`, отвечает 503 (Mini App) или текстом ошибки (TG).

**Why:** Две независимые причины:
1. **Истекший токен.** OAuth-токен в `/root/.claude/.credentials.json` (общий с CELPIP и `claude` CLI) живёт ~8 часов. Просрочился — refresh не сработал.
2. **Stale in-process cache (фикс 2026-05-02).** TG-бот и web-сервис — два процесса с общим credentials.json, но КАЖДЫЙ держит `_token_cache` в `bot/llm.py:33`. Когда один рефрешит токен (старый отзывается на сервере), второй процесс продолжает использовать старый из своего кеша → 401, хотя файл свежий. Симптом: `jq expiresAt` показывает токен валидным на много часов вперёд, но 401 всё равно прилетает. Видно по логам, что бот стартовал давно (часы назад), а web-сервис недавно перезапускался.

**How to apply:**
1. `jq '.claudeAiOauth | {expiresAt, mins:((.expiresAt - (now*1000))/60000|floor)}' /root/.claude/.credentials.json`
   - mins ≤ 0 → причина #1: истёк. `systemctl restart voice-tutor voice-tutor-web` — при следующем запросе пойдёт refresh.
   - mins > 60, но 401 всё равно → причина #2: stale cache.
2. `tail /root/voice-tutor/logs/{tutor,web-systemd}.log | grep -i "401\|invalid x-api-key"` — подтверждение.
3. Для причины #2: `systemctl restart voice-tutor voice-tutor-web` (оба!) — в новом процессе кеш чистый.
4. С 2026-05-02 в `bot/llm.py::call_claude` добавлен auto-recovery: при `anthropic.AuthenticationError` сбрасывает кеш через `get_anthropic_key(force_refresh=True)` и ретраит запрос один раз. Так что причина #2 теперь должна самовосстанавливаться без рестарта — но если самовосстановление не сработало (refresh-токен мёртв), всё равно нужен `claude` CLI re-login.

**Связанный антипаттерн:** другой агент / @DexClaudCodAIBot может попытаться "починить" запуском orphan-uvicorn на 0.0.0.0:8003 в обход systemd — порт занят, systemd не стартует, проблема усугубляется. Перед `systemctl start` всегда `ss -tlnp | grep 8003`.
