---
name: mai-assistant
description: MyPersonalAIassistent — личный AI-ассистент Артёма (отдельный от Тимы). 3 ящика + лендинг-заявки в @solo_inboxBot. https://github.com/InfinitySudo/MypersonalAIassistent
metadata: 
  node_type: memory
  type: project
  originSessionId: eb2acf2d-6373-4894-a23c-0c81abe522d7
---

## Где живёт
- **Локально:** `/root/MypersonalAIassistent/`
- **GitHub:** https://github.com/InfinitySudo/MypersonalAIassistent (приватный)
- **БД:** `/root/MypersonalAIassistent/mai.db` (отдельно от Тиминой `emails-optimization/emails.db`)
- **TG-бот:** `@solo_inboxBot` (id `8915185922`), owner chat_id `504609639`

## Сервисы (systemd)
- `mai-api.service` — FastAPI на 8093, принимает POST /api/agency-leads
- `mai-poller.service` — IMAP-poll каждые 5 мин (POLL_INTERVAL_SEC=300)
- `mai-bot.service` — Telegram UI, в т.ч. публичная /demo команда
- `mai-morning-digest.timer` — 06:30 Calgary daily

## 3 IMAP-ящика (multi-account)
1. `borysiukartem55@gmail.com` (label=personal-55) — UID range 100M-199M
2. `borysiukartem1990@gmail.com` (label=personal-1990) — UID range 200M-299M
3. `artempm@threestonesalliance.ca` (label=tsa-work) — UID range 300M-399M

Lead-form rows: UID ≥ 1_000_000_000 (никогда не пересекаются с IMAP).

## Стек скопирован из /root/emails-optimization (Тима)
- `agent.py`, `agent_db.py`, `agent_handlers.py` — Claude planner с approval workflow
- `pull.py`, `gmail_client.py`, `smtp_client.py` — IMAP fetch + SMTP reply
- `triage.py` — Claude Haiku classifier (urgent/reply/delegate/mute)
- `cards.py`, `dashboard.py`, `followups.py`, `morning_digest.py`
- `claude_auth.py` — OAuth через `/root/.claude/.credentials.json` (НЕ ANTHROPIC_API_KEY)

## Изоляция от Тимы
| Аспект | MAI | Tim |
|---|---|---|
| БД | `mai.db` | `emails.db` |
| TG-бот | `@solo_inboxBot` | другой |
| Юниты | `mai-*` | `emails-*` |
| Конфиг | `/root/MypersonalAIassistent/.env` | `/root/emails-optimization/.env` |

2026-05-22 убрал зеркало Артёма из Тиминого .env (`TG_OWNER_CHAT_ID=0` — backup в `/tmp/emails-optimization.env.bak-20260522`).

## Публичный /demo
В `app/bot.py` добавлен `cmd_demo` + `on_demo_callback` (pattern=`^demo:`) **выше** owner-check. Любой пользователь:
1. Получает intro + sample карточку (vendor invoice $4 280)
2. Жмёт ✅/✏️/🤖/👤/🔇 — callback отвечает текстом, **не пишет в БД и не шлёт SMTP**

CTA лендинга → `t.me/solo_inboxBot?start=demo` (Telegram сам подставит /demo).

## How to apply
- Запуск нового сервиса: `systemctl enable --now mai-*`
- Откатить зеркало Тиме (если Артём попросит): `cp /tmp/emails-optimization.env.bak-20260522 /root/emails-optimization/.env && systemctl restart emails-poller`
- НИКАКОГО `ANTHROPIC_API_KEY` — OAuth через `claude_auth.py` читает Claude Code creds
