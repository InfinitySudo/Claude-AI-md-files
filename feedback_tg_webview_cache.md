---
name: telegram-webview-aggressively-caches-mini-app-multi-layer-bust-needed
description: TG mobile WebView ignores ?v= query params and weak Last-Modified headers — to force fresh shell reload you need no-store HTTP header AND ?v= on script src AND per-render URL parameter on WebApp button. Otherwise users see stale UI for days.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f4c4861-fd60-4f57-b7af-c4260e03075c
---

При деплое UI правок в TG Mini App **TG mobile** часто продолжает показывать старую версию даже после закрытия и реоткрытия. Это **жёсткий cache на устройстве**. Desktop TG обновляется быстрее (другая cache policy), mobile — нет.

**Three-layer fix (все нужны вместе):**

1. **Backend: index endpoint выдаёт `Cache-Control: no-store`:**
   ```python
   @app.get("/")
   async def index():
       return FileResponse(
           STATIC_DIR / "index.html",
           headers={
               "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
               "Pragma": "no-cache",
               "Expires": "0",
           },
       )
   ```
2. **HTML: ?v= cache-bust на JS/CSS src** (статические assets могут кэшироваться раз HTML свежий):
   ```html
   <script src="/static/app.js?v=1778874000" defer></script>
   <link rel="stylesheet" href="/static/style.css?v=1778874000" />
   ```
3. **Bot keyboard / MenuButtonWebApp URL с per-render epoch:**
   ```python
   def _webapp_url_cachebust() -> str:
       import time
       sep = "&" if "?" in WEBAPP_URL else "?"
       return f"{WEBAPP_URL}{sep}v={int(time.time())}"
   # use in InlineKeyboardButton(web_app=WebAppInfo(url=_webapp_url_cachebust()))
   # and в set_chat_menu_button (refreshed at bot startup)
   ```

**Но даже это не пробивает уже закэшированную копию на устройстве пользователя.** Если у юзера сейчас стоит старая версия — нужно ОДНО ИЗ:
- TG → Settings → Data and Storage → Storage Usage → **Clear Cache** (можно selective по чату с ботом — безопаснее, не трогает media других чатов)
- Удалить чат с ботом → /start заново (last resort)

**Why:** 2026-05-15 — добавили Tools toggle в voice-tutor Mini App. Production endpoint отдавал новый HTML (verified через curl), TG desktop увидел сразу, TG mobile **держал старую версию 6+ часов** даже после полного reopen Mini App. Помогло только Clear Cache в TG mobile settings.

**How to apply:**
- При любых UI правках Mini App обязательно обновлять `?v=` в HTML script/css src — не оставлять старый epoch
- При создании нового Mini App с самого начала ставить `Cache-Control: no-store` на index route
- При troubleshooting "user не видит new UI" в первую очередь спрашивать — desktop или mobile, и предлагать Clear Cache до того как искать code bug

Связано: [[project_voice_tutor]], [[feedback_tg_persistent_keyboard]].
