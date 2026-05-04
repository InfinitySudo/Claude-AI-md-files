---
name: Mobile-dev workflow (CLAUDE.md per project + MOBILE_RULES.md)
description: 2026-05-02 — Артём настроил структурный mobile-dev workflow чтобы избегать OpenClaw-style потерь контекста; CLAUDE.md в каждом активном проекте; общие правила в /root/.claude/MOBILE_RULES.md
type: project
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
**Что:** Якорная система для mobile-разработки через `claude-telegram-bot`. Любой агент-сессия должна **сначала** прочитать `MOBILE_RULES.md` + `<project>/CLAUDE.md`, потом действовать. Это защищает от потерь контекста, которые ломали OpenClaw.

**Файлы:**
- `/root/.claude/MOBILE_RULES.md` — 11 общих правил (один агент на проект, plan mode для >3 файлов, voice-for-intent/text-for-names, commit как чекпоинт, report-every-destructive-op, read-memory-first, state-first-check-before-trust, stop-at-ambiguity, no-secrets-committed, memory-sync-on-commit, когда mobile-dev работает плохо)
- `<project>/CLAUDE.md` — специфика каждого проекта: что это, стек, ключевые файлы, команды, memory-якоря, можно/нельзя, mobile-specific

**Где есть CLAUDE.md** (создано 2026-05-02):
- `/root/voice-tutor/CLAUDE.md`
- `/root/4BotsBybit-Trading/CLAUDE.md` ⚠ PROD trading
- `/root/4BotsBybit-Documentation/CLAUDE.md`
- `/root/ontime/CLAUDE.md` ⚠ PROD TSA
- `/root/Wrestling-Performance-Tracker/CLAUDE.md` ⚠ PROD клиенты
- `/root/English-Teacher-CELPIP/CLAUDE.md`
- `/root/solo_claude_bot/CLAUDE.md`
- `/root/claude-telegram-bot/CLAUDE.md` ⚠ мета — ломая, ломаешь канал связи
- `/root/Claude-AI-md-files/CLAUDE.md`

**Bot-side изменения:**
- `claude-telegram-bot/claude_bot.py` system prompt начинается с «ПЕРВОЕ ДЕЙСТВИЕ В ЛЮБОЙ СЕССИИ» → инструкция читать MOBILE_RULES + project's CLAUDE.md перед действием
- Команда `/projects` в боте — one-screen overview: `📘 имя | git: clean/dirty | svc: N/M up`. Использовать чтобы видеть состояние всего перед стартом работы

**How to apply:**
- Когда работаешь mobile через claude-telegram-bot → бот сам прочитает нужные файлы
- Когда создаёшь новый проект → **сразу** добавляй `CLAUDE.md` по шаблону (см. voice-tutor/CLAUDE.md)
- Когда меняешь правила mobile-dev → правь только `MOBILE_RULES.md`, все CLAUDE.md ссылаются на него
- При reset/clear бота → агент снова прочитает файлы при первом запросе

**Why это работает:**
1. Якорь контекста переживает session reset
2. Single source of truth для правил
3. Visible-by-design — Артём видит что бот прочитал (бот пишет «🔧 читаю /root/.../CLAUDE.md»)
