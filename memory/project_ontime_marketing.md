---
name: OnTime Marketing Video Pipeline
description: Полный pipeline для маркетингового видео OnTime — где файлы, как пересобрать, что Артём выбрал в финальной версии.
type: project
originSessionId: 27d1f047-ee71-403c-890c-181c769d7af9
---
## Где
`/root/ontime/marketing/` — отдельный модуль внутри ontime, не в git.

```
marketing/
├── scripts/
│   ├── scenes.py            # SOURCE OF TRUTH: список сцен, narration, actions
│   ├── gen_audio.py         # Piper TTS на каждую сцену → audio/*.wav
│   ├── record_app.py        # Playwright: app-сцены (нужен системный python3, не .venv)
│   ├── record_overlays.py   # Playwright: overlay-сцены (HTML → mp4)
│   └── auth.py              # mint JWT для Playwright (admin user_id=4)
├── overlays/                # HTML для overlay-сцен (1080p, fixed-time animations)
├── audio/*.wav              # Piper output
├── clips/<id>/<id>.mp4      # Снятые видеоклипы (по одному на сцену)
├── music/*.mp3              # Kevin MacLeod tracks (CC BY 4.0): cheery / inspired / carefree
├── music/bed.wav            # Скомпилированный 9:25 music bed с crossfades
├── output/seg_<id>.mp4      # Сцены с озвучкой (voice mux)
├── output/voice_only.mp4    # Concat всех seg_*.mp4
├── output/ontime_promo.mp4  # Финал с music+ducking
└── voices/en_US-ryan-high.* # Piper модель
```

**Опубликовано:** `https://ontime.management/marketing-video/ontime_promo.mp4` (nginx alias на `/root/ontime/marketing/output/`, добавлен 2026-05-04 в /etc/nginx/sites-enabled/ontime location /marketing-video/). Прямая ссылка для отправки клиентам — не SPA-route, а static. Старый путь `/marketing/ontime_promo.mp4` НЕ работает (uxодит в SPA fallback).

## Pipeline (как пересобрать)

```bash
cd /root/ontime/marketing
.venv/bin/python scripts/gen_audio.py            # piper TTS, в .venv
python3 scripts/record_app.py                     # системный python3 (нужен playwright + jose)
python3 scripts/record_overlays.py
# затем mux+concat+ducking — см. ниже
```

**Critical:** `record_app.py` и `record_overlays.py` запускать через **системный** `python3`, не `.venv` — playwright/jose там не установлены. `.venv` только для piper.

## Composite (voice + ducking + music)

```bash
# 1) Mux voice into each clip с padded audio whole_dur=video_duration
for s in $SCENES; do
  vd=$(ffprobe ... clips/$s/$s.mp4)
  ffmpeg -i clips/$s/$s.mp4 -i audio/$s.wav \
    -filter_complex "[1:a]apad=whole_dur=$vd[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -shortest output/seg_$s.mp4
  echo "file '$(pwd)/output/seg_$s.mp4'" >> /tmp/concat.txt
done

# 2) Concat
ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy output/voice_only.mp4

# 3) Music ducking (sidechaincompress)
ffmpeg -i output/bed_trimmed.wav -i output/voice.wav \
  -filter_complex "[1:a]asplit=2[v1][v2];\
    [0:a][v1]sidechaincompress=threshold=0.06:ratio=8:attack=10:release=400:makeup=1[ducked];\
    [ducked][v2]amix=inputs=2:duration=longest:weights=1.0 1.4[mix]" \
  -map "[mix]" output/final_audio.wav

# 4) Final mux
ffmpeg -i output/voice_only.mp4 -i output/final_audio.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -shortest output/ontime_promo.mp4
```

## Финальная версия (что Артём выбрал)
- **25 сцен / ~6:45**: Hook → Old Way → Modules → Roles → Field (×4) → Materials/Procurement (×4) → Project Mgmt (×4) → Service & Equipment (×3) → Telegram → People & Reporting (×4) → Recap → CTA
- **Без цифр в voice** (UI цифры остаются — они в кадре)
- **Telegram** (не WhatsApp) везде
- **"Built for TSA"** на hook + CTA (БЕЗ "by TSA")
- **Без Admin** в roles matrix (5 ролей: Director/VP/PM, Purchasing/Accountant, Foreman, Installer/Helper, Service/Delivery/Mechanic)
- **Music**: ducking под voice (-15dB)
- **CTA**: "Open it now, and enjoy the app." (с apad для Piper)

## Зависимости системы
- `apt-get install fonts-noto-color-emoji` — иначе emoji в overlay рендерятся как квадратики
- `pip install playwright python-jose`
- `.venv` — только piper-tts, numpy, onnxruntime
- Voice model: `voices/en_US-ryan-high.onnx` (+ .json)
- Music tracks взяты с incompetech.com (Kevin MacLeod, CC BY 4.0)

## record_app.py поддерживает:
- `{"goto": "/path", "wait": 1000}`
- `{"scroll_to": 400, "wait": 1000}`
- `{"click": "selector"}`
- `{"text_click": "Tab Name"}` ← добавлено для табов в Procurement (Invoices)

## How to apply
- Чтобы поправить одну сцену: edit scenes.py + overlay HTML → re-gen только её audio (single piper) → re-render только её clip → re-mux её segment → re-concat → re-mix music → re-mux final.
- Для нового видео OnTime: переиспользовать pipeline, сменить scenes.py.
- Для других продуктов: скопировать `/root/ontime/marketing/` в `/root/<product>/marketing/`, поправить URL в record_app.py, JWT в auth.py.
