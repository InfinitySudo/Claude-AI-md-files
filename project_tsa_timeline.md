---
name: OnTime (TSA)
description: PWA для siding-компании TSA — контроль дедлайнов/часов по объектам, соревновательный рейтинг форманов; домен ontime.management
type: project
originSessionId: 7031998e-8b2e-4d12-b09a-35222914509f
---
## OnTime (бренд; внутри для компании TSA)

Мобильный PWA для Форманов компании TSA (установка сайдинга в Канаде). Главная задача — контролировать дедлайны и часы по объектам + соревновательный рейтинг форманов.

### Роли
- `admin` — Артём (первый зарегистрированный = admin, создаёт компанию; создание объектов только у admin)
- `foreman` — coach-эквивалент, один основной на объект
- `installer` — athlete-эквивалент
- Helper-форман / helper-installer — дополнительные участники, добавляет основной форман или admin

### Стек и порты
- Frontend: React 19 + Vite + Tailwind v4 + Leaflet (vanilla)
- Backend: FastAPI + SQLite (`backend/tsa.db`), JWT, bcrypt 4.2.1, **port 8002**
- systemd: `ontime-api.service` (enabled)
- nginx: `/etc/nginx/sites-available/ontime` → serves `/root/ontime/dist`, прокси `/api/` → 127.0.0.1:8002
- Домен: **https://ontime.management** (Let's Encrypt, auto-renew), также `www.ontime.management`
- DNS: A/AAAA на apex и www → 187.77.148.44 / 2a02:4780:5e:ba32::1
- Nominatim OSM для автокомплита адресов

### Что готово (step 1 + step 2)

**Step 1 — вкладка «Объекты»:**
- Список карточек: hours progress bar (зел<70 / жёлт 70–95 / красн >95 или overdue), timeline bar (days_passed/total_days), статус-чип, фильтры All/Active/Overdue/Done, FAB "+" у admin
- Создание: адрес с автокомплитом → draggable pin, radius slider 50–300м (default 120), даты, hours_budget, siding_type (vinyl/metal/hardie/wood/stucco/other), foreman (один), installers (мульти)
- Детальная страница: Overview (map с кругом радиуса, команда), Hours (placeholder), Settings (admin edit)
- i18n EN/RU toggle в хедере; PWA manifest + basic SW

**Step 2 — соревновательная система:**
- Формула points: base = +50 за срок, +5/день раньше (cap +50), -30 просрочка; +30 за бюджет, +1/час сэкон (cap +50), -1/час перерасход (cap -30); `size_mult = max(1, hours_budget/40)`; points = round(base * size_mult)
- Helper foreman получает 30% от полных очков
- `POST /api/projects/{id}/complete` {actual_hours} — admin закрывает объект, пишет в `project_scores` (по строке на участника), прорейт по дням если форман менялся
- `DELETE /api/projects/{id}/complete` — откат в 48h
- Helpers: `POST/DELETE /api/projects/{id}/helpers`, доступен основному форману и admin
- Смена основного формана: admin через PATCH (+ reason), пишет в `project_foreman_history`
- Rankings: `/api/rankings?period=week|month|year|all` + `/api/rankings/badges`
- Frontend: страница Rankings (подиум 🥇🥈🥉 + таблица), 🏆 чип у лидера недели, Add-helper modal, Complete-modal с preview breakdown, Settings форма смены формана

### Схема БД (SQLite)
```
companies(id, name, created_at)
users(id, role, full_name, phone, email, password_hash, company_id, avatar_url)
projects(id, company_id, name, address, lat, lng, geofence_radius_m=120,
         start_date, deadline, hours_budget, siding_type, foreman_id,
         status=planned, qr_token, notes,
         actual_hours, closed_at, prev_status)
project_installers(project_id, installer_id)
project_helpers(id, project_id, user_id, role[foreman_helper|installer_helper], added_by, added_at, removed_at)
project_foreman_history(id, project_id, foreman_id, from_date, to_date, reason, changed_by)
project_scores(id, project_id, foreman_id, points, breakdown_json, closed_at, is_helper)
```

### Step 3 — прогресс (2026-04-15)
- ✅ Регистрация через QR-код работает
- ✅ QR check-in/out через `/api/checkin` + сессии в `work_sessions` (start/end coords, duration_minutes)
- ✅ Геофенс enforcement: `_haversine_m`, /api/checkin отклоняет если dist > geofence_radius_m (admin обходит)
- ✅ `hours_spent` агрегируется из `work_sessions` (closed + live портion открытых) — `enrich_project`
- ✅ Complete: `actual_hours` опционален, по умолчанию = sum(work_sessions); auto-close открытых сессий при complete
- ✅ HoursTab: progress bar vs hours_budget + per-installer totals (●=активная сессия) + таблица сессий

### Step 3 — добавлено (2026-04-15, продолжение)
- ✅ Heartbeat: `sweep_stale_sessions` авто-закрывает open-сессии >12h; warning push at 9h via TG bot
- ✅ InstallerHomePage: summary today/week/month + in-memory cache for instant tab switch
- ✅ Auto-detect языка: `getLang` → navigator.language → uk/ru/en

### Step 4 — (2026-04-15..16)
- ✅ **TG Bot** (`backend/tg_bot.py`, systemd `ontime-bot.service`): /start /status /checkout; push via `backend/notify.py`
- ✅ **Login via Telegram**: 6-digit code flow (POST /api/auth/tg/request → POST /api/auth/tg/verify); admin invite code `TSAdmin2026`
- ✅ **Photo reports**: POST/GET/DELETE /api/projects/{pid}/photos; upload resize 1600px JPEG; gallery+fullscreen in Photos tab
- ✅ **CSV export**: accountant-friendly (Edmonton TZ, H:MM, AM/PM); pay period bi-weekly (anchor Apr 19, 2026); scope mine/all_on_projects
- ✅ **Reports page** `/reports`: admin + foreman, scope toggle, pay period buttons with date labels
- ✅ **Team page** `/team`: Members tab (directory+assign) + Whitelist tab (admin roster mgmt); merged Roster here
- ✅ **Roster**: edit employee (name/TG/role), archive/restore (soft-delete), added_by tracking on project_installers
- ✅ **Shift system** for service/delivery: POST /api/me/shift/start|end|stops; ShiftPage at /shift; auto pseudo-project per worker
- ✅ **Project types**: cladding/masonry/service/delivery; shift_start_time + timezone for punctuality
- ✅ **Punctuality points**: +1 per on-time worker check-in; merged into Rankings
- ✅ **Geofence**: enforce on check-in only; check-out always allowed
- ✅ Stable JWT secret in systemd env; SW killed; in-memory cache (`src/lib/cache.js`); fmt util (`src/lib/fmt.js`)
- ✅ Dark login bg; logo cropped clean (diagonal mask); 3-language nav; desktop scroll fix

### Конфигурация
- `TSA_JWT_SECRET` in systemd ontime-api.service
- `TSA_BOT_TOKEN` + `TSA_ADMIN_INVITE_CODE=TSAdmin2026` in `/root/ontime/backend/.env.bot`
- Pay period anchor: 2026-04-19, 14 days
- Bot: @TSAOnTimeBot, systemd `ontime-bot.service`
- nginx: `/uploads/` proxied to API, `/assets/` immutable cache, `/index.html`+`/sw.js` no-cache

### Git
- Remote: https://github.com/InfinitySudo/OnTime.git (private)
- Latest commit: `710184a` step 4 (2026-04-16)

### Stubbed (step 5+)
- Team tab content (Артём определит)
- Photo upload from shift stops (reuse project photos infra)
- Overtime / pay rate calculations
- Admin dashboard (company overview)

### Ключевые файлы
- `/root/ontime/backend/main.py` — all endpoints
- `/root/ontime/src/App.jsx` — router + header + nav
- `/root/ontime/src/pages/{LoginPage,ProjectsPage,ProjectDetailPage,RankingsPage}.jsx`
- `/root/ontime/src/components/{MapPicker,AddressAutocomplete,ProjectForm}.jsx`
- `/root/ontime/src/lib/i18n.js`
- `/etc/systemd/system/ontime-api.service`
- `/etc/nginx/sites-available/ontime` (Certbot SSL управляет ssl-блоком)

### Запуск/деплой
```
# backend — systemd managed
sudo systemctl restart ontime-api
sudo systemctl status ontime-api
# логи
journalctl -u ontime-api -f

# frontend — собрать и задеплоить
cd /root/ontime && npm run build
# nginx сам отдаёт /root/ontime/dist
```

### Git
Локально `git init` + коммиты. Remote НЕ настроен — Артём ещё не дал команду публиковать на GitHub.

**Why:** Артём — владелец TSA, хочет контролировать дедлайны/часы и устраивать соревнование между формами (лучший форман недели/месяца/года). Тот же подход что wrestling (coach=foreman, athlete=installer, QR check-in).
**How to apply:** добавлять функционал постепенно; step 3 = QR + check-in + геофенс enforcement + time-tracking с реальным `hours_spent`.
