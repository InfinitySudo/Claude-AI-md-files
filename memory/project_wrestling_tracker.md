---
name: Wrestling Performance Tracker
description: Mobile-first wrestling club app — training check-in, norms, tournaments, rankings. Live at constantwrestling.cloud
type: project
originSessionId: 4bfb864e-fbeb-4b9f-992a-5d9d840d8c81
---
## Overview
PWA-приложение для борцовского клуба Артёма. Coach + Athlete роли, QR check-in, нормативы с рангами, турниры.

## Stack
- **Frontend:** React 19 + Vite 8 + Tailwind v4 + shadcn-style components + Framer Motion
- **Backend:** Python FastAPI + PostgreSQL (DB: `wrestling_tracker`, user: `wrestling_user`)
- **Mobile:** PWA (installable) + Capacitor config ready for APK
- **Hosting:** VPS 187.77.148.44, nginx :443 (HTTPS Let's Encrypt)
- **Domain:** https://constantwrestling.cloud (cert auto-renews)
- **Repo:** https://github.com/InfinitySudo/Wrestling-Performance-Tracker (private)

## Key Files
- `/root/Wrestling-Performance-Tracker/` — project root
- `backend/main.py` — FastAPI (all endpoints, DB init on startup)
- `src/pages/` — HomePage, AthleteDashboard, CoachDashboard, AnalyticsPage, TournamentsPage, MembersPage, RankingsPage, LoginPage, SessionPage
- `src/components/athlete/QRScanner.jsx` — camera QR via html5-qrcode
- `src/api/client.js` — API client (JWT auth)
- `capacitor.config.json` — Android/iOS config
- `.github/workflows/build-android.yml` — CI for APK

## Services
- `wrestling-api.service` — FastAPI on :8001
- nginx `/etc/nginx/sites-enabled/wrestling` — HTTPS :443 + HTTP→HTTPS redirect
- DB password: `wrestling_pass_2026`, JWT secret in systemd env

## Features Done
- Auth: JWT, athlete (free) + coach (invite code `COACH2026`)
- QR check-in (camera + manual)
- Points: monthly + yearly, auto-reset
- 12 standard wrestling norms (pull-ups, push-ups, sit-ups, squats, rope climb, sprint 30m, box jumps, broad/vertical jump, circuit training)
- Rank system: Bronze 3+ / Silver 6+ / Gold 9+ / Champion 12+ norms confirmed
- Coach: assign/confirm/revoke norms, create sessions, generate QR, delete members
- Tournaments: create, weight classes 20-125kg, register athletes, matches, geo-location via GPS
- Analytics: weekly activity chart, streak, norms progress, points breakdown
- Members list with search/filter + delete (coach-only)
- Rankings (club leaderboard)
- PWA: manifest, service worker, installable on iPhone/Android
- GitHub Actions: auto-build Android APK on push

## Known Issues / TODO
- Ошибка при подтверждении норматива ("The starting did not...") — нужно проследить
- APK билд через GitHub Actions — проверить что artifact скачивается
- Push-уведомления (iOS 16.4+ поддерживает)
- Фото/видео в training analysis submissions
- Bracket auto-generation для турниров
- Club management (создание клубов, привязка атлетов к клубу)
- Coach review flow (grading submissions)

**Why:** Артём — тренер по борьбе, хочет трекать прогресс атлетов, посещаемость, нормативы и турниры через мобильное приложение.
**How to apply:** Проект живёт отдельно от trading bots. Код в /root/Wrestling-Performance-Tracker/, бэкенд на :8001, фронтенд через nginx.
