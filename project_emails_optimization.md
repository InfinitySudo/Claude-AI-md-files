---
name: Emails Optimization
description: AI-секретарь для входящей почты — триаж Claude + управление через TG; репо emails-optimization
type: project
originSessionId: f06d9554-9cc1-46e7-aaf0-3f92102afc52
---
**Что:** AI-секретарь для 6 бизнесов Артёма. **Клиент: Tim** (TG ID `7584033783` — отложен, тестируем на Артёме). Начали с одного email (Todorovassistant@gmail.com), который обслуживает 3 бизнеса Тима:
- **Todorov Couriers Ltd.** — Amazon DSP (доставка пакетов)
- **Reliance Rentals Ltd.** — аренда промышленного оборудования
- **NAC's Playhouse Ltd.** — арендная недвижимость + land development

Структура с keywords/domains в `/root/emails-optimization/businesses.json`. Триаж должен сначала классифицировать email по бизнесу, потом по urgency.

**Onboarding-вопросы Тиму** в `docs/client_questions.md` (отослать 2026-05-07). Ждём от него: project list (Dan case, Jack case, Stonegate, Cassels, ...), key contact emails по каждому, morning digest time.

## Состояние на 2026-05-06 (вечер — onboarding-волна от Тима)

**Готово и работает в проде:**
- Stage 1: IMAP pull → SQLite
- Stage 2: Claude Haiku 4.5 triage
- Stage 3: TG bot UI (6 кнопок)
- Stage 4: SMTP send-back в тот же thread
- Continuous poller (60s) + systemd
- Mirror: @TodorovAssistantBot (Артём, TEST_MODE=1) + бот Тима (LIVE)
- Pinned dashboard auto-update
- /help рендерит `docs/tim_user_guide.md`
- A1 Follow-up tracker (daily 9:00 timer + /followups)
- B1 HTML body cleaner
- C2 Snooze 24h button
- **Stage 6 (2026-05-06):** Project tags из `projects.json` — 4 матера: stonegate (Dan), jack_rentals, cassels_umbrella, couriers_ops + general fallback. Contact emails Bennett Jones (RomaniukP, ivelinaterzieva83, DouglasA) пересекаются Stonegate/Jack — disambiguator по keywords в system prompt.
- **Stage 7 (2026-05-06):** Urgent subcategories: legal/money/deadline/amazon/tenant/other. Карточка показывает sub-emoji + бейдж только для класса urgent.
- **Stage 8 (2026-05-06):** Morning digest 07:00 Calgary — `app/morning_digest.py` + systemd timer. Top 10 emails by class priority + recency, single TG message в каждый mirror.

**systemd units (все active):**
- emails-bot.service (Артём, TEST_MODE=1)
- emails-bot-tim.service (Тим, LIVE)
- emails-poller.service (60s)
- emails-followups.timer (OnCalendar=09:00 daily)
- emails-morning-digest.timer (OnCalendar=07:00 daily)

**DB schema:** добавлены колонки `project_id`, `urgent_subcategory` (миграция в `db.init()`); индекс `idx_emails_project`. Старые ~6750 писем — без project_id (NULL); только новые получат теги. Можно при желании сделать one-shot re-triage только по pending non-mute (~1089 писем).

**Ещё НЕ сделано:**
- Stage 5: Delegate forwarding к ассистенту (нужен TG_ASSISTANT_USERNAME + чат от Тима)

**Последний commit:** `bea2c29` (stages 6/7/8)
**Репо:** github.com/InfinitySudo/emails-optimization (private)
**Live VPS пути:** `/root/emails-optimization/`, БД `/root/emails-optimization/emails.db`

**Why:** У Артёма 6 бизнесов / 6 email-ящиков, нужна сортировка, авто-ответы на неважное, драфты на важное, делегирование одному помощнику. Полный auto-send опасен (галлюцинация = потерянный клиент), поэтому human-in-the-loop через TG.

**How to apply:**
- Репо: `/root/emails-optimization`, на GitHub `InfinitySudo/emails-optimization` (private, ветка main)
- Стек: Python + IMAP/SMTP (Gmail App Password) + SQLite + Claude Haiku 4.5 + python-telegram-bot + systemd
- **Pivot 2026-05-05:** OAuth выкинули — Google консольно ломал redirect_uri даже после Web-app + порта + Playground; App Password сработал с первой попытки. Если позже понадобится Pub/Sub push — вернёмся к OAuth.
- Этапы (один коммит на этап): (1) Gmail OAuth + pull, (2) Claude triage, (3) TG UI карточки, (4) Send-back, (5) Delegate flow с дедлайнами
- MVP: 1 email = `Todorovassistant@gmail.com` (выбран 2026-05-05), 1 помощник, 1 TG-чат с топиками (топик = бизнес). Масштабирование по факту работы.
- Triage классы: urgent / reply / delegate / mute. Mute идёт в дайджест 1 раз/день, не пушит.
- Auto-send только для mute-класса; reply/urgent/delegate — всегда через approve-кнопки в TG.
- Первые 1-2 недели всё через approve, копится feedback для уточнения system prompt.
- Креды живут в `.env`: `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD` (App Password из myaccount.google.com/apppasswords с включённым 2-Step), `TG_BOT_TOKEN`, `TG_OWNER_CHAT_ID`, `ANTHROPIC_API_KEY`.
