---
name: Tim AI Agent — расширение emails-optimization (план + текущее состояние)
description: AI-делегат для Тима внутри его TG бота; Week 1+2 production-ready 2026-05-08, остался только Calendar OAuth (Week 3)
type: project
originSessionId: 58e3834e-1b62-4ea5-bd65-3c76fe531f55
---
**Что это:** Расширение `emails-optimization` бота — AI-агент, которому Тим
делегирует задачи. Каждое внешнее действие требует confirm Тимом через
inline button. Расширение существующего `emails-bot-tim.service`, не отдельный бот.

**КРИТИЧНО:** Tim — only English. См. `feedback_tim_english_only.md`. Все
user-facing strings, docs, email drafts → English.

**Service:** `emails-bot-tim.service` (chat=7584033783). Параллельный
mirror `emails-bot.service` (Артём, TEST_MODE=1) делит ту же
`emails.db` — изоляция через `owner_chat_id` (см.
`feedback_emails_two_bots_shared_db.md`).

---

## Что live прямо сейчас (commit dde6fce, 2026-05-08)

**Команды (8):**
- `/delegate <text>` + voice / photo / PDF
- `/tasks` — открытые задачи
- `/agent_help` — quick reference
- `/memory`, `/remember pref.tone = friendly`, `/forget pref.tone` — per-owner persistent prefs, инжектятся в каждый planner-prompt
- `/cost [day|model]` — Claude spend (today/7d/30d/all-time)
- `/auth_status` — Claude OAuth health (expiresAt + refresh_token)

**Approval cards 4 кнопки + ✍️ Reply на ask_owner:**
- ✅ Apply → реальный SMTP-send (Gmail) или task_*/close_no_action
- ✏️ Edit → "type instruction" → Claude rewrite payload → re-render card
- ⏭ Skip / ❌ Cancel — idempotent (двойной тап = одна отправка)
- ✍️ Reply на ask_owner → ответ → replan_with_answer → новые actions на той же task'е

**Hints в TG (балансированно, не отвлекает):**
- AI Agent блок в `/start` (счётчик открытых только если >0)
- Welcome-card на самый первый `/delegate` (один раз навсегда)
- Footer-tip на ПЕРВОЙ карте каждого action_type (`send_email`,
  `create_event`, `ask_owner`, `task_create`) — single-shot per owner
- Internal `_tip` kind скрыт от planner и от `/memory`

**Fault-tolerance:**
- Sonnet rate-limit / 5xx → fallback на Haiku (RateLimitError + APIStatusError 529/503/502)
- OAuth 401 → дружелюбная карта с "claude auth login on VPS"
- orphan in_progress >120s на startup → cancelled
- per-model pricing table — Haiku не считается по Sonnet ценам
- httpx/httpcore логи WARNING+ — никакого getUpdates спама
- Edit/Reply state TTL 5/10 min, voice/photo/PDF дропают state с уведомлением

---

## Файлы

- `app/agent.py` — planner (Sonnet→Haiku chain), `rewrite_action_payload`, `replan_with_answer`, `MODEL_PRICING`
- `app/agent_db.py` — schema + per-owner CRUD + memory + `cancel_orphan_in_progress` + `position_in_task` + `count_tasks`
- `app/agent_handlers.py` — все commands + approval flow + Edit/Reply state machine + tips
- `app/bot.py` — `_set_commands` с 8 agent-commands + AI block в `/start` + httpx silence
- `app/smtp_client.send_reply()` — переиспользуется агентом для send_email
- `app/claude_auth.get_client()` — OAuth с auto-refresh (уже было)
- `docs/tim_user_guide.md` — `/help` source-of-truth, обновлено для всех Week-2 фич
- `docs/tim_agent_intro.md` — onboarding doc (без markdown-таблиц для пересылки)
- `docs/agent_plan.md` — оригинальный 4-недельный план

---

## Что ещё TODO (Week 3+)

1. **Google Calendar OAuth** — последний stub. `_execute_action` для
   `create_event`/`move_event` логирует "would do X". Нужен
   `app/calendar_client.py` с OAuth flow + CRUD.
2. **🤖 Agent handle button** на triage cards — чтобы
   forward email-card в agent одним тапом (упоминалось в Week 2,
   ещё не сделано).
3. **Web search tool** — `gmail_search` / `calendar_list` /
   `calendar_free_slots` пока stubs в `_exec_read_tool`.
4. **Morning briefing + weekly review** — Week 4.

---

## Open questions для Тима (висят в intro doc)

1. Default email tone (formal/friendly/adaptive)?
2. Block-list (whom never to reply to)?
3. Whitelisted domains for autonomous web_fetch?
4. Morning briefing time (default 8am Calgary)?
5. Reminder format (text / button-snooze)?

Когда Тим начнёт тестить и ответит — записать через `/remember pref.*`.

---

**Costs estimate:** ~$30-50/мес LLM (Sonnet planner + Haiku fallback). 50 задач/день — пока непроверено, /cost покажет реальность.

**Не путать:** wife-english-tutor (для жены) — отдельный проект, на паузе.
