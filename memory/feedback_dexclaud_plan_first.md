---
name: dexclaud-plan-first
description: claude-telegram-bot (DexClaudCodAIBot) теперь обязан составлять план через create_plan + показывать live progress; Opus 4.7 жёстко для code/bug/fix
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f70afc19-ea49-486a-8c9e-b332332d417d
---

# @DexClaudCodAIBot работает по плану и только Opus 4.7

**Артём 2026-05-16:** «научи бота перед задачей составлять чёткий план, следовать ему, показывать прогресс в TG как в Claude Code status-line. И haiku-балабол не должен касаться кода — только Opus 4.7».

**Why:** Бот терял контекст посреди работы, спамил 15 tool-call сообщений за раз, иногда падал на Haiku которая валила многошаговые планы.

**How to apply:**

## Что есть в боте сейчас (после 6 коммитов 2026-05-16)

1. **Tools `create_plan(title, steps)` + `update_progress(current_step)`** — бот ОБЯЗАН вызвать их для любой задачи где шагов >1. Перед `create_plan` сначала `read_file` на `<project>/CLAUDE.md` если задача про конкретный проект.

2. **Live progress UI** — edit-in-place один TG-message:
   ```
   🔧 *Title*
   ▰▰▰▰▰▰▰▱▱▱▱▱ 67% · 2m 14s · ↑8.4k
   [✓] (1/6) ...
   [▶] (2/6) ...
   [○] (3/6) ...
   ```

3. **Auto-status fallback** — даже если бот забыл `create_plan`, status_callback всё равно редактирует один message «🔧 Работаю...» вместо спама.

4. **Жёсткий Opus 4.7 для code/trading.** `CODE_PATTERNS` ловит русский, английский, латиницу (`ne rabotaet`/`pochini`/`dobav`), project names (`voice-tutor`/`wife-english-tutor`/...), paths (`/root/`/`.py`/...). `/sonnet` и `/haiku` **не работают** для code — override на Opus. Fallback chain отключён.

5. **Retry-after на rate-limit** — до 3 ретраев на тот же Opus с retry-after из заголовка. Показывает `⏳ Opus rate-limit · жду 15s · ретрай 2/3`.

## Когда квота Claude Code исчерпана

5h-квота **общая** для Opus+Sonnet+Haiku на OAuth-плане. Fallback бесполезен. Бот покажет:
> Opus 4.7 rate-limit держится более минуты. На Claude Code 5h-квота общая для всех моделей — fallback не поможет. Подожди до сброса (~5h от первого запроса).

Альтернатива (если упор регулярно) — отдельный `ANTHROPIC_API_KEY` с per-token billing вместо OAuth.

## Файлы

- `/root/claude-telegram-bot/claude_bot.py` (~1700 lines после модификаций)
- Сервис: `claude-telegram-bot.service` (systemd, active)
- Token: `CLAUDE_BOT_TOKEN` env var
- Owner: `OWNER_ID = 504609639`
- GH: `InfinitySudo/Claude-Telegram-Bot` main

## Если бот не делает план

1. Проверь модель — должна быть `🔥 opus` в конце ответа, не `⚡ haiku` или `🧠 sonnet`
2. Если `🧠 sonnet` на code-вопрос — значит CODE_PATTERNS не сматчил → добавить новый паттерн
3. Если план не создан, но бот делает много tool-calls — он проигнорировал SYSTEM_PROMPT правило №1, нужно перетянуть выше или сделать ещё императивнее

См. также:
- [[session-2026-05-16-bot-modernization]] — полный лог сессии
- [[dexclaud-bridge-bot]] — бот также используется как notification bridge (sendMessage без интеракции)
