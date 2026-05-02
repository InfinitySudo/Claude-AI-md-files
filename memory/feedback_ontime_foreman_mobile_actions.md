---
name: OnTime Foreman Mobile Actions
description: Форман на мобильном теряет primary-action кнопки — `hidden lg:inline` режет подписи, иконки тонут в шапке
type: feedback
originSessionId: 45b2c078-a10f-4965-bf3f-1c14531042ed
---
Когда добавляю primary-action в OnTime PWA — дублировать на главную страницу роли, не полагаться на header-иконку.

**Why:** 27 апреля 2026 Богдан (форман, Pixel) полчаса не мог найти "Scan QR" — кнопка была только в `App.jsx` header как Camera-иконка, текст `hidden lg:inline` (≥1024px) на телефоне скрывался, иконка тонула среди ~12 других. У инсталлера на `InstallerHomePage` была большая кнопка сверху, у форемана на `ProjectsPage` — нет. Background: foreman home = ProjectsPage (список проектов), installer home = InstallerHomePage (большая Scan QR + список сессий). Когда добавлял кнопку только инсталлеру — упустил, что форман тоже нуждается.

**How to apply:**
- Любая primary-action кнопка для installer'а → проверить нужна ли foreman'у; если да — добавить и на ProjectsPage, и на ProjectDetailPage (форман часто работает изнутри проекта).
- В шапке (`App.jsx`) `hidden lg:inline` для foreman = невидимо на любом телефоне; не считать это решением.
- При фиксе — `npm run build` в `/root/ontime`, nginx сразу подтягивает (no-cache на index.html). SW не кеширует ассеты.
