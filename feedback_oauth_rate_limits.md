---
name: OAuth rate-limits & "Лимит исчерпан"
description: Все боты Артёма share один OAuth token; opus/sonnet quotas в 5h окнах; trading_request заблокированный fallback ломал interactive UX; фикс 2026-05-02
type: feedback
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
**Правило:** Никогда не блокируй fallback chain жёстко по типу запроса — Anthropic Max имеет 5h cap на opus/sonnet, при исчерпании единственный путь к ответу это haiku. Лучше degraded ответ с пометкой «[⚡ haiku вместо 🔥 opus]», чем глухая дверь.

**Why:** В `claude-telegram-bot/claude_bot.py` была защитная логика:
```python
if trading_request:
    models_to_try = [MODEL_OPUS]  # fallback запрещён
```
Идея — «лучше упасть, чем тихо даунгрейдить». Но при реальном rate-limit это превращалось в полный отказ всех trading-запросов (а почти все запросы Артёма помечались как trading из-за перекошенного system prompt). Ждание 5 минут / часа / суток не помогало потому что фоновые `bybit-claude-hourly` (5×/день) + `bybit-claude-watchdog` (5×/день) непрерывно жрут квоту.

Live-тест 2026-05-02 12:00 показал: Opus + Sonnet → `rate_limit_error`, Haiku → ✓. То есть quota опустошена ровно на Opus/Sonnet, Haiku свободен — но fallback на него не срабатывал.

**How to apply:**
1. **В коде ботов**: разрешать fallback chain для всех запросов, маркер ответа `[label вместо primary_label]` сигнализирует пользователю degraded mode
2. **В расписании автономов**: hourly + watchdog = главные пожиратели; смотреть `/etc/systemd/system/bybit-claude-*.timer` `OnCalendar`. Раньше 10 запусков/сутки → стало 5 (1 hourly + 4 watchdog) после 2026-05-02
3. **Архитектурно**: фоновые многошаговые agents с opus/sonnet — антипаттерн при OAuth подписке. Заменять на deterministic скрипты с узким haiku-вызовом только когда нужен judgment (см. `project_hourly_supervisor.md`)
4. **Долгосрочно**: добавить `ANTHROPIC_API_KEY` fallback — interactive на OAuth, фоновые на pay-per-token API. Не сделано пока, но опция остаётся.

**Все процессы что share `/root/.claude/.credentials.json`:**
- `claude-telegram-bot.service` (interactive)
- `voice-tutor.service` + `voice-tutor-web.service` (interactive)
- `English-Teacher-CELPIP` боты (Артём + Лилия)
- `solo-claude-approve.service`
- `bybit-claude-hourly.service` (фоновый, после 2026-05-02 — Python скрипт, Claude только при event'ах)
- `bybit-claude-watchdog.service` (фоновый)
- Любой ad-hoc `claude` CLI запуск
