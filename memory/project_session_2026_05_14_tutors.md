---
name: session-2026-05-14-tutors
description: Big session — wife/son tutor overhaul (OAuth fix + live tools + 6-level CEFR library + EWA-style UI + Alyona avatar + SadTalker on PC1 GPU)
metadata: 
  node_type: memory
  type: project
  originSessionId: 684f23a1-5fd6-499b-a3a9-251bef4fdb6b
---

Большая сессия 2026-05-14 с Артёмом. Запушено 6 коммитов в 3 репо.

**wife-english-tutor** (4 коммита, master):
- `41d974c claude: oauth force-refresh + tool-use + live tools + translate` — [[feedback_oauth_force_refresh]] + [[project_tutor_live_tools]]
- `6fba398 tts: route to PC1 Kokoro with OpenAI fallback + startup voice-routing log` — [[feedback_tutor_tts_wiring]]
- `6387e6b library: 6 CEFR levels + 5 categories + 11 new books + EWA-style /read` — A1-C2 + Fairy/Classics/Adventure/Career/Conversational, GA-style chips, anim banners
- `fee0c7c ui: Alyona hero avatar + welcome video + drawer + translate + repeat-drill` — hamburger drawer, large avatar (50vh), welcome MP4 со звуком при первом клике, tap-to-translate + 🎙 Repeat after me на каждом teacher-bubble

**son-french-tutor** (1 коммит, main):
- `23983ff claude+library+ui: oauth force-refresh + 6 CEFR levels + categories + /read filters` — те же фичи но FR + книги (ma-famille A1, le-chat-botte A1, tom-sawyer B1, comte-monte-cristo B2, etranger C1)

**voice-tutor** (1 коммит, main):
- `a79faab oauth: force-refresh on 401 must hit refresh API, not just reread disk`

**SadTalker инфра:**
- ПК1 (`tkach@100.99.211.123`, RTX 3090, Windows): SadTalker ALREADY installed в `C:\Users\tkach\SadTalker` + `sadtalker_venv`. 235-frame 1024² видео на GFPGAN ~3-4 мин. Запуск через `powershell -File C:\Users\tkach\Documents\sadtalker_*.ps1`.
- ПК2 (`borys@100.73.22.1`, RTX 3090): SadTalker install был запущен (`launch_pc2_install.ps1`) но статус неясен — проверить если понадобится PK2 fallback.
- `lilia_welcome.mp4` сгенерён из `/tmp/assistants/assistant_03.png` (рыжая женщина у окна, gen 12 мая) + Kokoro TTS audio; H.264 baseline + AAC обязательны для TG и iOS Safari, иначе чёрный экран.

**Что Артём попросил уточнить:**
- Лилия = жена/ученица; Алёна = AI-учительница (англ.). Не путать в text/UI.
- Тим бот English-only (см. [[feedback_tim_english_only]]) — НЕ относится к Лилии.
- Книги по теме EWA: разделы как у EWA app — банеры + cover-карточки.

**Открытые TODO:**
- Seed для wife отдельных новых книг шёл при rate-limit на Sonnet → Haiku fallback; некоторые A1 главы получились 65-91 слов (ниже целевых 80-120) — Haiku недостаточно точно держит word-count. Можно повторить отдельные книги когда Sonnet вернётся.
- Pronunciation drill использует /api/pronounce который уже был. Не проверял что target=полная фраза teacher-bubble работает идеально (drill изначально для коротких target из FIX-тегов).
- SadTalker на ПК2 install — status неизвестен, надо допилить чтобы был backup GPU.
