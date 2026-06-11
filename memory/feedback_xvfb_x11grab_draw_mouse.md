---
name: feedback_xvfb_x11grab_draw_mouse
description: ffmpeg x11grab под Xvfb падает «Failed to query xcb pointer» — нужен -draw_mouse 0
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8f237bfa-fef6-41c3-a76d-e5a48bcdb71c
---

При записи экрана `ffmpeg -f x11grab` под headless **Xvfb** (нет аппаратного указателя мыши)
ffmpeg валится с `Failed to query xcb pointer` / `Error during demuxing: Generic error in an
external library` и пишет обрубок в несколько секунд (а плеер при этом отыграл нормально).

**Why:** x11grab по умолчанию пытается захватить курсор; на Xvfb запрос XFixes-указателя падает.

**How to apply:** добавить `-draw_mouse 0` в команду x11grab (до `-i $DISPLAY`). Фикс внесён в
`/root/gerchik_recon/capture_one.sh` 2026-06-11 — добил 2 PLAY-FAIL урока курса Герчика (757c3cc2,
59b89de9), курс стал 82/82. Симптом «PLAY OK, но mp4 ~4.6с/247KB» = именно это. См. [[project_gerchik_strategy_extraction]].
