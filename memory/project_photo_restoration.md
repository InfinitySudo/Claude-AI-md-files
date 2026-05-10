---
name: Photo restoration pipeline (CPU-based on VPS, paused)
description: Установлен GFPGAN+RealESRGAN+LaMa+DeOldify+SadTalker в /root/photo_ai_venv; pipeline работает на CPU очень медленно — кандидат на миграцию на GPU homelab
type: project
originSessionId: ba8718ff-04fd-4b45-b897-9e35cdddc20f
---
**Контекст 2026-05-07:** знакомая Артёма попросила реставрировать и оживить старое ч/б фото (мужчина с трофеем-рогами на фоне реки, главная диагональная трещина по верхней трети). Скачали с Google Drive. Сделали полный pipeline на CPU, отправили результаты в `@AISmartFriendBot`.

**Стек установлен на VPS:**
- `/root/photo_ai_venv/` — отдельный venv с torch 2.5.1+cpu + torchvision 0.20.1+cpu
- GFPGAN + Real-ESRGAN (face restore + bg upscale) — патч basicsr `functional_tensor → functional`
- `simple-lama-inpainting` (без iopaint — он pin'ит сломанный Pillow) — context-aware inpainting
- `/root/DeOldify/` — git clone + fastai==1.0.60 + IPython + yt-dlp; модель ColorizeStable_gen.pth (834 MB) с huggingface (deepai mirror был мёртв); фикс `Path()` вместо str для root_folder
- `/root/SadTalker/` — talking-head animation; checkpoints в `/root/sadtalker_models/` через симлинки (чтобы re-clone не потерял); 4 numpy 2.x фикса в `src/face3d/util/preprocess.py` и `src/utils/preprocess.py` (np.VisibleDeprecationWarning, np.float→float в astype/dtype, `.item()` для array→scalar conversions)

**Pipeline что работает:**
1. **Stage 1 LaMa** — авто-маска через Frangi vesselness filter — слабо для трещин (путает с рогами/листвой)
2. **Stage 2 GFPGAN + Real-ESRGAN x2** — отличное качество, лицо чёткое, детали сохранены, 1680×2560
3. **Stage 3 DeOldify Stable** — реалистичная раскраска
4. **Stage 4 LaMa с ручной polygon-маской** — главная диагональная трещина убрана успешно
5. **Stage 5 SadTalker** — анимация лица с silent audio, `--still --preprocess full --enhancer gfpgan`. **На CPU занял 50+ минут**. Output в MPEG-4 ASP — Telegram не играет, нужно ffmpeg → libx264 + faststart перед отправкой.

**Артефакты (на VPS):**
- `/tmp/photo_artem.jpg` — оригинал
- `/tmp/photo_stage4_final.jpg` — финал статика (1680×2560, цвет, без трещины)
- `/tmp/sadtalker_out/2026_05_07_18.06.23/photo_stage4_final##anim_audio_full.mp4` — анимация MPEG-4
- `/tmp/animation_h264.mp4` — anumacja для TG (1.2 MB)

**Скрипты:**
- `/tmp/restore_photo.py` — conservative cv2 pass (без AI, для быстрых преsмотров)
- `/tmp/photo_pipeline.py` — full AI 3-stage
- `/tmp/inpaint_crack_v2.py` — Stage 4 ручная маска (координаты трещины захардкожены)
- `/tmp/colorize_only.py` — DeOldify standalone

**Memory: Артём 2x RTX 3090 дома (Windows, дети-геймеры 10-12 лет вечерами).** Этот CPU-pipeline — кандидат на миграцию на GPU. На 3090 каждый stage = секунды/минуты вместо десятков минут.

**Disk impact:** ~5 GB (DeOldify 800M + SadTalker 2.5G + photo_ai_venv 1.5G + GFPGAN models 700M).
