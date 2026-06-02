---
name: project_wrestling_appstore_screenshots
description: "Wrestling App Store скриншоты — Playwright-скрипты review_screens/{iphone,ipad13}.mjs + demo-аккаунт; регенерят реальные экраны в точные размеры одной командой"
metadata: 
  node_type: memory
  type: reference
  originSessionId: b2df2c3a-76aa-4633-8aa8-f7effcfd029d
---

**Зачем:** Apple отклонял Constant Wrestling по Guideline 2.3.3 (скриншоты не показывали реальный UI — стояли промо-картинки). Решение — генерить скриншоты живого приложения автоматически, чтобы при каждом ресабмите перегенерить за минуту.

**Где:** `/root/Wrestling-Performance-Tracker/review_screens/`
- `iphone.mjs` — генерит iPhone 6.9″ (CSS 430×932 @3 = **1290×2796**) в `iphone-67/` и iPhone 6.5″ (414×896 @3 = **1242×2688**) в `iphone-65/`.
- `ipad13.mjs` — генерит iPad 13″ = **2064×2752** (`ipad13-*.png`).
- Запуск: `cd review_screens && node iphone.mjs` / `node ipad13.mjs`. Playwright chromium из `~/.cache/ms-playwright/chromium-1217/` (executablePath захардкожен — проверить версию при ENOENT).

**Demo-аккаунт ревью** (логин внутри скриптов, POST `/api/auth/login`, токен → `localStorage.wpt_token`):
`demo-promo@constantwrestling.cloud` / `DemoReview2026!` — наполнен данными, показывает реальные экраны. Этот же аккаунт даём ревьюеру Apple.

**Экраны (route → имя):** `/rankings` лидерборд, `/tournaments` спарринги, `/members` состав, `/` панель тренера, `/competitions` соревнования, `/profile` карта борца. Все — рабочий UI с нижней навигацией, без splash/login (именно это требует Apple).

**Грабли App Store Connect (2026-05-30):**
- Отдельной секции 6.7″ больше нет — слилась в **«6,9-дюймовый дисплей»**; файлы 1290×2796 туда подходят.
- Apple масштабирует загруженные 6.9″ и 6.5″ на меньшие экраны сам; остальные секции (6.3/6.1/5.5…) необязательны.
- При замене: «Удалить все» в секции → «Выбрать файл». Размеры мешать нельзя.
- iPad 13″ покрывает ревью; iPad 12,9″ необязателен.

**⚠ dist стирается при `npm run build`** — публичные zip кладутся в `dist/` и слетают; **PNG-исходники держать в `review_screens/`, не в dist**. Сам скрипт пишет именно в review_screens.

Связано: [[feedback_wrestling_capacitor_uploads_img]], [[project_session_2026_05_27_wrestling_v1_0_submit]].
