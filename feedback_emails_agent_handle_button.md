---
name: emails-agent-handle-button
description: 🤖 AI Plan button on every triage card → fires Claude planner with email thread context; lives in bot.py:_build_keyboard + poller.py:_send_card + agent_handlers.start_email_delegation
metadata: 
  node_type: memory
  type: project
  originSessionId: e259f10c-4218-4b83-a0fd-cb861ccaa1f1
---

`act:agent:<uid>` callback в triage card вызывает AI-планнер с email body как extra_context. Без явного `/delegate`.

**Why:** До 2026-05-12 у Тима AI-agent был зарегистрирован, но никто его не звал — 0 записей в agent_tasks. Артём попросил довести до рабочего состояния через Option B из docs/agent_plan.md.

**How to apply:**
- Кнопка появляется только на новых карточках (старые в TG без неё).
- В TEST_MODE (Артёмов mirror) кнопка отвечает "(test) would hand to AI agent" без обращения к Claude.
- Gmail-thread reading и Calendar tools — stub'ы; планнер видит только email body из SQLite.
- Source задачи: `email:<uid>`, `source_email_id=<uid>` — для трассировки.
- Sonnet 4.6 регулярно 429-ится; fallback на Haiku 4.5 уже встроен в `agent.plan_for_request`.

Связано с [[emails-two-bots-shared-db]] и [[tim-agent-plan]].
