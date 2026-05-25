---
name: agency-landing
description: "Лендинг RU-SMB agency на ontime.management/agency — 7 пакетов, форма заявки, 3 кейс-видео, кликабельные карточки. Запущен 2026-05-22."
metadata: 
  node_type: memory
  type: project
  originSessionId: eb2acf2d-6373-4894-a23c-0c81abe522d7
---

## Где живёт
- **URL:** https://ontime.management/agency/
- **Файлы:** `/root/landing/agency/` (НЕ git репо)
  - `index.html` — 7 пакетов + кейсы + процесс + FAQ + форма заявки
  - `styles.css` — mobile-first, тёмная case-секция
  - `script.js` — smooth-scroll, mobile-menu, форма-POST, click-anywhere-on-case
  - `videos/{ontime,email_assistant,wrestling}_promo.mp4` + постеры
- **nginx:** `/etc/nginx/sites-available/ontime` — `location ^~ /agency/` (no-cache HTML/CSS/JS, max-age=86400 на videos), `location ^~ /api/agency-leads → 127.0.0.1:8093`

## 7 пакетов на лендинге
1. Field Ops Tracker (OnTime) — $1500 + $300/мес
2. CRM-автоматизация — $2-3k + $500/мес
3. AI голосовой ассистент — $3-5k + $800-1500/мес
4. Custom AI-интеграция — $80-120/ч
5. Wrestling / Sports Tracker — $2k + $200/мес
6. Hourly Insights (бывший «Hourly Supervisor» — слово «надзиратель» убрано) — $1200 + $150/мес
7. Invoice OCR + Catalog Sync — $800 + $100/мес

## 3 кейса с видео
- 01 **OnTime** — http://ontime.management/ — `ontime_promo.mp4` (60с)
- 02 **AI email-ассистент** — `t.me/solo_inboxBot?start=demo` — `email_assistant.mp4` (50с) ([[mai-assistant]])
- 03 **Wrestling Tracker** — http://constantwrestling.cloud/ — `wrestling_promo.mp4` (50с)

Каждая `<article class="case" data-href="...">` кликабельна целиком через JS (HTML5 forbids `<a>` around `<video controls>`).

## Форма заявки
POST `/api/agency-leads` → FastAPI на `127.0.0.1:8093` (`mai-api.service`) → пишет в `mai.db` как `lead-form+<uuid>@ontime.management` с UID ≥ 1_000_000_000, pre-triage `urgent` + project=`agency_lead`, TG-нотификация в `@solo_inboxBot`.

## How to apply
- Если Артём говорит «лендинг сломан» — первая проверка: `curl -skI https://ontime.management/agency/` (Cache-Control должно быть `no-cache, must-revalidate`)
- Cache-bump policy: bumpить `?v=N` на `styles.css`, `script.js`, и **каждый видео/poster URL** при изменении. Без этого браузеры держат старые 24ч (`max-age=86400`)
- При правке текста копий — обновлять и narration в [[mai-video-pipeline]], иначе video/text расходятся
