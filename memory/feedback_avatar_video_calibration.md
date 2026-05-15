---
name: avatar-video-calibration
description: "OpenCV Haar cascade автоопределяет scale + y-offset чтобы голова на SadTalker/Wav2Lip output matched то же место на статичной фотке. Recipe — снять frame ffmpeg, detect face bbox в обоих, посчитать `scale = photo_face_h / video_face_h`."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Rule:** При склейке статичной photo с SadTalker/Wav2Lip video в одном UI frame (talking_loop overlay) не подбирай scale на глаз — Haar-cascade определит точно за 100ms.

**Why:** Артём ловил "голова крупнее в видео" / "голова мельче в видео" — на глаз scale всегда промахивается на 5-15%. SadTalker `--preprocess crop` обрезает video сильнее (face ~62% высоты) чем оригинальная фотка (~44% высоты), поэтому нужен ~0.71 scale.

**Recipe:**
```python
import cv2
det = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def face_bbox(p):
    img = cv2.imread(p)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fs = det.detectMultiScale(g, 1.1, 5, minSize=(50,50))
    x,y,w,h = max(fs, key=lambda f: f[2]*f[3])
    return y, y+h, h, img.shape[0]

# Extract frame from video
# ffmpeg -y -i video.mp4 -frames:v 1 frame.jpg
photo_top, photo_bot, photo_h, photo_H = face_bbox('photo.jpg')
video_top, video_bot, video_h, video_H = face_bbox('frame.jpg')
photo_face_ratio = photo_h / photo_H
video_face_ratio = video_h / video_H
scale = photo_face_ratio / video_face_ratio
y_pad = int((photo_top/photo_H - (video_top*scale)/(video_H*scale)) * video_H * scale)
```

**Then ffmpeg:**
```bash
ffmpeg -y -i video.mp4 -vf "scale=iw*${SCALE}:ih*${SCALE},pad=${OUT_W}:${OUT_H}:(${OUT_W}-iw)/2:${Y_PAD}:color=0x${BG_HEX}" \
  -an -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p -movflags +faststart out.mp4
```

**Verify after:** запусти Haar detect на первом кадре out.mp4, сравни face_top / face_height с фоткой. Дельта должна быть <2% по top, <3% по height — это invisible переход.

**Important:** padding background должен совпадать с CSS gradient stage. У son-french-tutor — `#e9c5a3` (peach).

**Не всегда хочется matched** — иногда close-up при speaking даёт UX "наклонилась поговорить" (Артём предпочёл это после калибровки). В таком случае используй raw native crop (no scale/pad) и `object-fit: cover` в square stage. Square aspect-ratio в `#avatar-stage` обязательно — landscape strip на desktop растягивает пустоту по бокам.

Memory cv2 версия 4.13.0 уже в `/root/voice-tutor/.venv` (наследие Wav2Lip era).
