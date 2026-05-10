---
name: emails-opt — два бота на одной БД, изоляция через owner_chat_id
description: emails-bot (Артём mirror, TEST_MODE=1) и emails-bot-tim (продовый Тим) работают через один app.bot и одну emails.db; любые новые таблицы должны нести owner_chat_id
type: feedback
originSessionId: 58e3834e-1b62-4ea5-bd65-3c76fe531f55
---
`/etc/systemd/system/emails-bot.service` и `emails-bot-tim.service` — оба
запускают `python -m app.bot`, оба регистрируют ВСЕ хендлеры (включая
`agent_handlers`), оба читают/пишут в один `emails.db`.

**Why:** До 2026-05-08 `agent_tasks/runs/actions` не имели `owner_chat_id`,
и Тим в `/tasks` видел тестовые задачи Артёма. То же касалось `agent_memory`
(не существовала вообще). Smoke-test показал — Sonnet в эту ночь был
rate-limited, fallback на Haiku сработал только после fix.

**How to apply:**
- Любая новая таблица для AI-агента → колонка `owner_chat_id INTEGER NOT NULL`
  + индекс по ней + ВСЕ helpers фильтруют по этому полю.
- TEST_MODE-бот должен отказываться от write-action'ов агента (см.
  `_start_delegation` early-return). На приёмке проверять обоими ботами.
- Я (Артём) = chat 504609639, Тим = chat 7584033783.
- На startup всегда вызывать `agent_db.cancel_orphan_in_progress(owner)`
  с порогом ≥120s — иначе торчат `in_progress` после крэша планера.
- Per-model pricing хранится в `agent.MODEL_PRICING`; обновлять при смене
  моделей, иначе cost-логи врут (Haiku в 4× раз дешевле Sonnet).
- При rate-limit обрабатывать `RateLimitError` И `APIStatusError` со status
  529/503/502 — `OverloadedError` приходит как APIStatusError, не как
  отдельный класс.
