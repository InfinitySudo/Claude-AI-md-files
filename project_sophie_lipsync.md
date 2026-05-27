---
name: sophie-lip-sync-via-sadtalker-on-pc1-in-progress
description: "Live talking avatar для @FrenchTuporBot/@EnglishTecherTutorBot — фотореалистичный портрет + лип-синк MP4 на каждый ответ; pipeline 2026-05-12, Wav2Lip миграция pending"
metadata: 
  node_type: memory
  type: project
  originSessionId: bee53ff8-706d-4515-9bd3-ee94e425b8a2
---

**Goal:** photoreal Sophie/Алёна/N8 actually speaks on every TG Mini App reply — не статичная фотка, а лип-синк video. Pipeline: Sophie text → OpenAI TTS → PC1 SadTalker MP4 (~2-3 мин) → `<video>` overlay в Mini App.

**Где работает (на 2026-05-12 18:40 MDT):**
- ✅ `@FrenchTuporBot` сын: full pipeline wired, dormant пока PC1 offline.
- ⏸️ `@EnglishTecherTutorBot` жена: ждёт фото Алёны Николаевны (Артём шлёт через `@DexClaud` с caption `save:alena`).
- ✅ `@AISmartFriendBot` (voice-tutor) с N8: avatar UI wired 2026-05-12. `#avatar-stage` с 3-state `<img>` (idle/thinking/speaking все указывают на один портрет 1024×1024) + halo-ring + listen-pulse + think-dots overlays. `setState()` в `app.js` обновляет `avatarStage.dataset.state`. Lipsync MP4 пока НЕ wired — VPS `web/app.py` не зовёт PC1 `:8003/lipsync` для voice-tutor (только son-french-tutor). Когда захотим лип-синк — повторить `_lipsync_blocking()` паттерн из `son-french-tutor/web/app.py` + добавить `<video id="avatar-video">` в frame + `playLipsyncVideo()` в JS.

**Status (важно для следующей сессии):**
1. PC1 (100.99.211.123) онлайн с 2026-05-12 (поздним вечером), `:8003/` отвечает 200.
2. **Sophie talking_loop.mp4** 2026-05-12 v3 (финал): SadTalker `expression_scale=1.4` + GFPGAN enhancer, 1024×1056, 46.2с, ~9 MB muted H.264. `WET_LIPSYNC_URL` закомментирован в `.env` — backend не зовёт PC1, loop играется в UI поверх TTS audio через `playReplyAudioWithLoop()` (`web/static/app.js`). Артём выбрал v1.4 после сравнения с v1.8 ("слишком гримасничает") и Wav2Lip ("зубы склеены/нет половины"). Wav2Lip без post-GFPGAN всегда выдаёт 512x512 mouth-region (модель predicts 96×96) — отсюда деградация.

**Команда воспроизведения loop (для замены/удлинения):**
```
# 1. TTS source ~45-60с французского текста (см. /tmp/sophie_60s.wav как образец)
# 2. POST на PC1 lipsync (теперь принимает expression_scale form param)
curl -X POST http://100.99.211.123:8003/lipsync \
  -F "image=@.../avatar/idle.jpg" -F "audio=@.../sophie_60s.wav" \
  -F "still=0" -F "enhancer=1" -F "expression_scale=1.4" \
  -o /tmp/loop_raw.mp4 --max-time 1200
# 3. Strip audio + faststart
ffmpeg -y -i /tmp/loop_raw.mp4 -an -c:v libx264 -preset slow -crf 23 \
  -pix_fmt yuv420p -movflags +faststart \
  /root/son-french-tutor/web/static/avatar/talking_loop.mp4
```
Server `lipsync_server.py` патчен: `expression_scale` теперь form-param (default 1.4), `subprocess.run(timeout=900)` подняли с 300 чтобы 46с audio с GFPGAN успевал (рендер ~11 мин на ПК1 GPU).
3. Артём недоволен качеством SadTalker: «губками шевелит, зубы склеены». Решение — **Wav2Lip** (designed for actual mouth open). Установка в процессе:
   - ✅ git clone `Wav2Lip` в `C:\Users\tkach\Wav2Lip`
   - ✅ wav2lip_gan.pth (435MB) → `Wav2Lip\checkpoints\`
   - ✅ s3fd.pth (89.8MB, 2026-05-12) → `Wav2Lip\face_detection\detection\sfd\s3fd.pth`. Источник: `https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth` (старый URL ВНЕЗАПНО работает). Magic bytes `80 02 8A 0A` = legacy pickle protocol 2.
   - ✅ Sample inference запущен прямо через `inference.py` без отдельного wrapper'а — sadtalker_venv (torch 2.5.1+cu121) совместим как есть. Output `/root/voice-tutor/web/static/n8_wav2lip_demo.mp4` доступен по `https://voice.constantwrestling.cloud/static/n8_wav2lip_demo.mp4` (6.5s аудио → 297KB MP4, ~25s на GPU).
   - ⏳ Server wrapper `wav2lip_server.py` (по образцу `lipsync_server.py`) — пока нет, для on-the-fly через VPS нужен `:8004/lipsync` или интеграция в существующий `:8003/lipsync`.

**Команда запуска inference (рабочая, 2026-05-12):**
```
cd C:\Users\tkach\Wav2Lip
C:\Users\tkach\sadtalker_venv\Scripts\python.exe inference.py `
  --checkpoint_path checkpoints\wav2lip_gan.pth `
  --face input\portrait.jpg --audio input\sample.wav `
  --outfile results\out.mp4 --static True --resize_factor 2
```
`--static True` — для одной фотки (использует первый кадр); `--resize_factor 2` ускоряет в 2× при минимальной потере качества.

**Pipeline (когда PC1 онлайн):**
- VPS `_lipsync_blocking()` в `/root/son-french-tutor/web/app.py` ловит TTS bytes, POST на PC1 `:8003/lipsync`, кеширует MP4 by sha256(portrait+audio).
- `web/static/index.html` имеет `<video id="avatar-video">` overlay над `.avatar-photo`. JS `playLipsyncVideo(b64, hasCorrection)` в `web/static/app.js`.
- nginx `/etc/nginx/sites-enabled/son-french-tutor`: `proxy_read_timeout 300s` + `proxy_send_timeout 300s` (поднял с 120s).
- `requests.post(timeout=(5.0, 300))` — fail-fast при offline PC1, иначе ждать lipsync до 300s.

**PC1 SadTalker pipeline (working as of 2026-05-12):**
- `C:\Users\tkach\sadtalker_venv\` — Python 3.11 + torch 2.5.1+cu121 + pinned: numpy==1.23.5, librosa==0.9.2, scipy==1.10.1, face_alignment==1.3.5, imageio>=2.30 (NOT 2.19 — recursion bug на 3.11), scikit-image 0.20+, basicsr 1.4.2 (с патчем `functional_tensor`→`functional`).
- Запуск: `C:\Users\tkach\start_lipsync.ps1` через WMI Win32_Process.Create (Start-Process от ssh умирает на disconnect, см. [[feedback_pc1_ssh_quirks]]).
- Текущий `lipsync_server.py` зашивает: `--preprocess crop --size 512 --expression_scale 1.4`, форма `enhancer=1` → GFPGAN.
- Output picked by **largest size** (intermediate MP4s — face crop only, мелкие).

**Известные проблемы SadTalker:**
- `preprocess=full` дал чёрный фон → переключил на `crop` (face-only).
- `imageio==2.19.3` имеет infinite recursion в plugin loader на Python 3.11 → `imageio>=2.30`.
- `basicsr.data.degradations` import `torchvision.transforms.functional_tensor` (removed) → sed-патч в venv site-packages.
- `np.float` removed в numpy 1.24 → нужен numpy<1.24, но 1.23.5 ОК.

**Что ещё в очереди (после возврата PC1):**
1. Завершить Wav2Lip install (s3fd + server) — Артём ждёт лучшего lip movement.
2. Сравнить SadTalker vs Wav2Lip — выбрать engine.
3. ✅ Avatar UI в voice-tutor для N8 (сделано 2026-05-12 — circle portrait + halo + state overlays; full-screen layout как у сына пока НЕ сделан, обычный stacked layout с orb ниже).
4. Когда Артём пришлёт фото Алёны (`/root/incoming/alena.jpg`) — resize в `/root/wife-english-tutor/web/static/avatar/idle.jpg`, restore `<img>` в `index.html`, possibly включить lipsync для неё тоже.

**Файлы изменены сегодня (committed):**
- `wife-english-tutor` master: persona Эмма→Алёна Николаевна, voice shimmer (для жены подруга, не Ethan); lessons.py restored after sed wipeout.
- `son-french-tutor` main: persona Lucas→Sophie+Парижанка; voice onyx→nova; reader Play/Pause/Stop+seekbar+auto-advance; full-screen Sophie + hamburger drawer; cache-bust на /static/; lipsync wiring (dormant).

**Не закоммичено:**
- `lipsync_server.py` локально в `/tmp/`, на PC1 в `C:\Users\tkach\SadTalker\`. Не git-tracked, не на VPS.
- Wav2Lip установка в `C:\Users\tkach\Wav2Lip\`.
- `nginx proxy_read_timeout 300s` (system config, не git).
