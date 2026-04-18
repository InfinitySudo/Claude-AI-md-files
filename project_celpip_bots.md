---
name: CELPIP Teacher Bots
description: Two Telegram bots (Artem CLB 10, Liliia CLB 7-8) for daily CELPIP-General prep in Calgary; voice-first
type: project
originSessionId: 5365f0ed-2b91-4f6b-90a2-8a6d90dc3dcd
---
Репо: `/root/English-Teacher-CELPIP` (https://github.com/InfinitySudo/English-Teacher-CELPIP)

**Why:** Artem и его жена Лилия готовятся к CELPIP-General в Калгари. Экзаменационная дата не назначена, но заниматься нужно каждый день. Артёму нужен CLB 9–10 (он ставит 10 как stretch), Лилии — 7–8.

**How to apply:**
- Код единый, два systemd-инстанса читают разные env: `celpip-bot@artem.service` + `celpip-bot@liliia.service`
- Env-файлы: `/root/English-Teacher-CELPIP/.env.artem` и `.env.liliia` (gitignored)
- `CELPIP_TARGET_CLB` управляет строгостью: те же таски, но system prompt калибрует model answer и требования под уровень
- Голос: Whisper STT → Claude (OAuth `/root/.claude/.credentials.json`, Sonnet 4.5 primary, Opus 4.1 для `/score`) → OpenAI TTS (onyx для Артёма, nova для Лилии)
- Команды: `/s1–/s8` Speaking, `/w1–/w2` Writing, `/r1–/r4` Reading, `/l1–/l6` Listening, `/score` (строгий разбор), `/mock` (WIP)
- Curriculum: `curriculum/tasks.py` (все таски с реальными CELPIP таймерами), `rubric.py` (CLB 1–12), `prompts.py` (target-aware)
- Telegram IDs: Artem=504609639, Liliia=1356240185
- TODO: SQLite progress (sessions, scores_history), `/mock` с таймерами, cron daily reminders, Listening через TTS из сгенерированных диалогов
