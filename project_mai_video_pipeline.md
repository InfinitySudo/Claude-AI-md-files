---
name: mai-video-pipeline
description: Как генерируются 3 кейс-видео для ontime.management/agency. gpt-4o-mini-tts + Playwright + ffmpeg + STT-validation.
metadata: 
  node_type: memory
  type: project
  originSessionId: eb2acf2d-6373-4894-a23c-0c81abe522d7
---

## Что и где
- **3 видео:** `/root/landing/agency/videos/{ontime,email_assistant,wrestling}_promo.mp4` (по ~50-60с, 1.4-1.5 MB каждое)
- **Narration scripts:** `/tmp/clean_narration.json` (чистый русский, без английских вкраплений)
- **Build scripts:** `/tmp/build_final.py`, `/tmp/rebuild_intros.py`, `/tmp/rebuild_wrestling_intro.py`
- **HTML overlays:** `/tmp/ontime_promo_new/overlays/*.html`, `/tmp/email_promo/overlays/*.html`
- **Audio segments (validated):** `/tmp/audio_v2/{ontime,email,wrestling}/*.mp3` + `stt_report.json`

## TTS-стек (рабочий)
- **API:** `https://api.openai.com/v1/audio/speech`
- **Model:** `gpt-4o-mini-tts` (НЕ `tts-1-hd` и НЕ PC1 local — см. [[feedback-tts-pc1-mandarin]])
- **Voice:** `nova` (молодой женский, тот же что использует @AISmartFriendBot когда падает в OpenAI fallback)
- **Instructions:** `"Говори чётко и спокойно по-русски. Естественные паузы между предложениями. Не торопись. Без иностранного акцента. Все цифры произноси словами. Английские имена бренда произноси по-русски, как написано."`
- **Key:** из `/root/voice-tutor/.env` → `OPENAI_API_KEY`

## Validation: STT-loop
Каждый сегмент после TTS прогоняется через Whisper-1 на `http://100.99.211.123:8001/v1/audio/transcriptions`. Token-set Jaccard similarity ≥ 0.85 = pass; < 0.85 → retry с `speed=0.92`.

⚠️ False-positives: outro-сегменты с английскими доменами (`ontime.management`, `constantwrestling.cloud`) — Whisper транскрибирует латиницей, similarity падает до 0.2-0.5, но **TTS произносит правильно**. Слушать ушами, не доверять только Whisper.

## Video-сторона
- **OnTime + Email:** HTML overlays (`<h1>`, `<h2>`, mock-карточки) → Playwright headless 1280×800 → record_video_dir → .webm → ffmpeg scale + libx264 crf24
- **Wrestling:** живой скринкаст `https://constantwrestling.cloud/` через Playwright, login как `demo-promo@constantwrestling.cloud` (creds в `/tmp/wrestling-demo.json`). Демо-юзер создан через `/api/auth/register` (coach + 3 demo athletes, invite code `P7HF03PT`)

## Audio-leading архитектура
Сначала генерится audio → измеряется duration → Playwright записывает ровно эту длину + 0.4с tail. ffmpeg mux с `-shortest`. **Не наоборот** — иначе обрезается аудио на полу-фразе.

## Грабли (решённые)
1. **«Это…» в каждом intro** — баналит, убрано 2026-05-22. Тексты теперь сразу с предметом: «OnTime — приложение…», «Ваш почтовый ассистент.», «Констант Рестлинг — приложение…»
2. **Языковой свитч на 中文** — в первой версии Playwright кликал random язык из ["Polski","中文","Українська",...]; теперь жёстко на RU (или EN для зеркала). Сцена 6 «navigation» НЕ переключает язык — только табы.
3. **Поляризация бренд-имён** — английские bare-bones (`Kojo`, `ClickUp`, `Excel`, `WhatsApp`) → русские эквиваленты («таск-трекеры, таблицы, бумажные счета, мессенджеры»)
4. **TSA имени и Tim's имени** — все убраны из видео; кейсы используют общие формулировки.

## How to apply
- Изменить narration → правка `clean_narration.json` → запуск `gen_validated.py` → `build_final.py`
- Изменить одну сцену → точечный rebuild через `rebuild_<x>_intro.py`-style helper
- Каждое изменение → bump `?v=N` ко **всем** видео и постерам в `/root/landing/agency/index.html` (см. [[agency-landing]])
