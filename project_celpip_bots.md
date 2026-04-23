---
name: CELPIP Teacher Bots
description: Two Telegram bots (Artem CLB 10, Liliia CLB 7-8) for daily CELPIP-General prep in Calgary; voice-first, with error tracking and adaptive drills
type: project
originSessionId: 5365f0ed-2b91-4f6b-90a2-8a6d90dc3dcd
---
Репо: `/root/English-Teacher-CELPIP` (https://github.com/InfinitySudo/English-Teacher-CELPIP)

**Why:** Artem и его жена Лилия готовятся к CELPIP-General в Калгари. Артёму нужен CLB 9–10, Лилии — 7–8. Лиля жаловалась что бот даёт мало и не помнит её ошибки — 2026-04-22 добавлены error_log, /daily, /focus, /stats.

**How to apply:**
- Код единый, два systemd-инстанса читают разные env: `celpip-bot@artem.service` + `celpip-bot@liliia.service`
- Env-файлы: `/root/English-Teacher-CELPIP/.env.artem` и `.env.liliia` (gitignored)
- `CELPIP_TARGET_CLB` управляет строгостью: те же таски, но system prompt калибрует model answer и требования под уровень
- Голос: Whisper STT → Claude (OAuth `/root/.claude/.credentials.json`, Sonnet 4.5 primary, Opus 4.1 для `/score`) → OpenAI TTS (onyx для Артёма, nova для Лилии)
- Drill prompts теперь требуют `[ERRORS]JSON[/ERRORS]` блок + `[CLB overall=N]` — парсятся в `error_log` и `task_attempts.score_clb`
- Команды:
  - `/s1–/s8` Speaking, `/w1–/w2` Writing (180-220 слов строго), `/r1–/r4` Reading (6-8 MCQ), `/l1–/l6` Listening (5-6 MCQ)
  - `/daily` — плана на день: по одному R+L+W+S, адаптивно (слабый навык → harder pick); `/next` — следующий невыполненный
  - `/focus [tag]` — прицельный дрилл на топ-категорию из `error_log` (10 упражнений)
  - `/stats` — средний CLB по навыкам + топ-5 ошибок + vocab + общее
  - `/score` (строгий разбор), `/mock` (WIP)
- Curriculum: `curriculum/tasks.py`, `rubric.py`, `prompts.py` (в `prompts.py` — `ERROR_BLOCK_INSTRUCTION` добавляется ко всем drill-промптам)
- Daily reminder (08:00 MST) агрессивно пушит `/words` если `total==0` или `added_today==0 && due<3`; всегда подталкивает `/daily`
- Telegram IDs: Artem=504609639, Liliia=1356240185
- TODO: `/mock` с таймерами, Listening через TTS из сгенерированных диалогов
