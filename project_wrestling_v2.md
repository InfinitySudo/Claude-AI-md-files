---
name: Wrestling App v2 — Multi-club + Full Features
description: Major v2 rewrite done 2026-04-13; multi-club, proportional norms, analysis, profile with socials, club branding
type: project
originSessionId: 4bf9c010-6bf6-4410-b91f-d3731633751f
---
## Wrestling Performance Tracker v2

### Стек (актуально на 2026-05-15)
- Backend: FastAPI :8001, systemd unit `wrestling-api.service`
- DB: **PostgreSQL** `wrestling_tracker` через `psycopg2.pool.ThreadedConnectionPool(2..30)` — не SQLite (миграция была раньше, старая запись врала)
- nginx: `/etc/nginx/sites-enabled/wrestling` — `/assets/` immutable 1y + gzip + no-cache на `index.html`/`sw.js`/`manifest.json`
- Запас по нагрузке: легко 200 активных юзеров на текущем VPS

### Что сделано (2026-04-13)

**Мультиклуб:**
- Таблица `clubs` (name, city, owner_coach_id, invite_code)
- Коуч при регистрации создаёт клуб (club_name + city обязательны)
- Атлет регистрируется по invite-коду клуба
- Все запросы фильтруются по club_id — полная изоляция
- `POST /api/clubs/regenerate-invite` — генерация нового кода

**Нормативы (переработаны):**
- Коуч создаёт: name, target_value, max_points (кнопки +/-)
- `publish_to_club=true` → создаёт для всех атлетов клуба
- Атлет вводит actual_value → `POST /api/norms/{id}/submit`
- Баллы = `min(max_points, (actual/target) × max_points)` — пропорционально
- Коуч confirm/reject → `POST /api/norms/{id}/confirm`
- Статусы: pending → submitted → confirmed/rejected

**Анализ тренировок:**
- Атлет выбирает тренировку + пишет текст → `POST /api/analysis`
- Коуч видит все submitted, ставит баллы + комментарий → `PATCH /api/analysis/{id}/review`
- Атлет видит отзыв и баллы

**Тренировки (расширены):**
- Поля: title, session_date, group_name, description
- QR-код автоматически (4 часа)

**Профиль атлета:**
- Фото (upload), имя, дата рождения, весовая категория, вес
- Соцсети: Instagram, TikTok, YouTube, Telegram, WhatsApp, Facebook
- Share Card: `GET /api/profile/card/{user_id}` (публичный)
- Ранг: Bronze(0-49) / Silver(50+) / Gold(100+) / Champion(200+)

**Баллы из 3 источников:**
- Нормативы: пропорционально (max задаёт коуч)
- Анализ: оценка коуча (0-N)
- Посещения: 1 за check-in

**Брендинг Constant Wrestling:**
- Логотип клуба: icon-192.png, icon-512.png (PWA иконки)
- Фон app: bg-watermark.png (красный волк, 10% opacity, cover)
- Фон логина: bg-login.png (20% opacity)
- Хедер: логотип + "Constant Wrestling"
- Источник: Google Drive файл с 5 вариантами логотипа

**Фронтенд:**
- LoginPage: выбор роли, коуч→создание клуба, атлет→invite код
- CoachDashboard: invite-код, создание тренировок/нормативов, confirm/reject, review analysis
- AthleteDashboard: 4 таба (Home/Norms/Analysis/Profile), bottom nav
- RankingsPage: лидерборд с разбивкой баллов по источникам
- Удалять участников может только coach

### Что добавлено 2026-04-14 (commit de061ab)
- **Sparrings вместо Tournaments** (только UI, endpoints остались `/api/tournaments` ради backward compat).
- Атлеты теперь видят вкладку Sparrings (6 иконок в bottom nav с уменьшенным padding).
- **Start time (HH:MM)** добавлен к training_sessions и tournaments (обе миграции в `ALTER TABLE ... ADD COLUMN IF NOT EXISTS start_time`).
- **PATCH /api/sessions/{id}** и **PATCH /api/tournaments/{id}** — coach-only, club-scoped, блокируются после наступления `session_date+start_time` (возвращается флаг `editable` в list/get для UI).
- Members page: тренер видит DOB→возраст, weight_kg, weight_class, фото; при раскрытии — соцсети.
- Sparring participants: backend JOIN users и сортировка по `weight_kg ASC` (fallback 9999 для без веса); UI показывает kg-бейдж.

**Удаление аккаунта:**
- Только coach может удалять участников
- Атлет НЕ может удалить сам себя (убрано по запросу Артёма)

### Ключевые файлы
- Backend: `/root/Wrestling-Performance-Tracker/backend/main.py`
- API client: `/root/Wrestling-Performance-Tracker/src/api/client.js`
- Frontend pages: `src/pages/` (Login, CoachDashboard, AthleteDashboard, Rankings, Members, Tournaments, Analytics, Session)
- Assets: `public/` (icon-192, icon-512, bg-watermark, bg-login, club-bg.jpg)
- URL: constantwrestling.cloud
- API: port 8001, systemd: wrestling-api

### Что добавлено 2026-05-19 (commit ddeee40) — Coach Toolkit
- **Club policy** — `club_policies` + `policy_acceptances`; коуч редактирует на `/policy`, версия растёт → атлет re-signs. Default Constant policy seeded.
- **User groups** — `user_groups` + `users.group_id` + CRUD endpoints; chip-фильтр и inline assign в Team.
- **Password reset** — `/api/auth/reset-request` + `/auth/reset-confirm`, токен 1h. `WPT_SMTP_*` env (на prod не настроено — токен в journald).
- **Live sparring scoring** — `sparring_scores` + `POST /api/tournaments/{tid}/score`; быстрые +/- кнопки во вкладке спарринга; учёт в leaderboard.
- **Birthday reminder daemon** — background-thread в FastAPI, 14:00–15:00 UTC ежедневно; уведомляет атлета + коучей через `_wp_notify`. Manual: `POST /api/admin/birthday-sweep`.
- **i18n** — react-i18next с EN/RU/PL; `LanguageSwitcher` в login footer.
- **Coach NormsPage** — отдельный matrix-таб (athletes × norms) + create + history; убрал inline-список с CoachDashboard.
- **RankingsWidget** — top-5 на CoachDashboard с разбивкой N/S/A/An.
- **Подробности**: см. [[session-2026-05-19-wrestling-coach-toolkit]].

### Что добавлено 2026-05-26 (commit 33bcc18) — Wrestler card + Competitions + Pro rating + Parental consent + Constant ToS
- **Wrestler card (карта борця)** — `users.{hometown,wrestler_level,year_started_wrestling,bio,card_shared_at,card_approved_at,card_approved_by,card_rejected_reason}`. ProfilePage hero «на свой лад»: rotating holo border, Constant red-triangle chip, country, ⚡N-win streak, ✓ verified от тренера. Tabs Home/Results. Share workflow: athlete → coach approve/reject → community-visible. Endpoints `/api/profile/{uid}/wrestler-card`, `/matches`, `/share-card`, `/api/coach/card-reviews`, `/api/profile/{uid}/review-card`.
- **Competitions (Соревнования)** — отдельная club-scoped вкладка `/competitions`: тренер постит выезд с fee/payment_link/instructions; атлет выбирает возраст+вес, submit→approve→mark paid. Только участники клуба видят roster.
- **Pro in-app rating** — `GET /api/pro/rating?country=&weight_class=&age_group=` агрегирует W/L/win_pct/BW% из finished tournament_matches с обеими сторонами=registered. `InAppRatingCard` в LigaProPage с фильтрами.
- **Parental consent под-18** — `RegisterBody` принимает `date_of_birth` + `parent_*`. Если age<18 → required parent name/email, token, email родителю с consent-link. `/parental-consent` страница + App.jsx `ConsentGate` блокирует UI пока родитель не подтвердил (poll /me 30s).
- **ToS / Privacy** — заменён generic `DEFAULT_APP_POLICY` на текст Constant Calgary Wrestling Club (PIPEDA, Alberta law); startup bump'ает версию.
- **Подробности**: [[session-2026-05-26-wrestler-card-competitions]].

### Что добавлено 2026-05-26 (commit 421573b) — Platform-policy + Geo + Camp verify + Sessions UX
- **App-wide policy** — `app_policies` + `users.app_policy_accepted_version`; `/api/app-policy` (public) и `/api/admin/app-policy` (super-admin update). **Тренер тоже подписывает** при регистрации.
- **Club-policy не auto-seed** — новые клубы получают пустой policy, тренер пишет сам.
- **Geo на регистрации** — `country` + `region` обязательны для всех; `timezone` авто из `Intl.DateTimeFormat`. 📍 use-my-location через Nominatim.
- **Camps admin-verify** — `contact_phone/email/country/region` обязательны, `socials_url` опц.; `admin_status='pending_admin'` → супер-админ approve/reject (`/api/admin/camps/{id}/verify`); фильтры по country в UI; бейдж PENDING/REJECTED.
- **Sessions** — `session_extra_tasks` + `session_signups` + `session_extra_task_confirms`; endpoints sign-up/roll-call/extra-task confirm; SessionPage с панелями Roll-call и Bonus tasks. Группа тренировки — All members или из `user_groups` (Manage Groups), без жёсткого Kids/Junior/Senior.
- **Analysis** — UNIQUE(session_id, athlete_email); upsert при submitted/rejected; reject через `coach_review='REJECT:…'` или `points_awarded<0` открывает повторную правку учеником.
- **Norms** — `/api/norms/finalize` батч-эвент: лидер=max_points, –1 за каждое место, overall ranking bonus синтетической строкой.
- **Sparring i18n** — `format_round_robin / format_single_elim / bracket_single_elim / matches_round_robin / regenerate_confirm` во всех 10 языках. TournamentsPage не имеет хардкода RU.
- **Leagues tours** — `<select>` 1..5 вместо `<input type=number>` в Create и Edit.
- **Client robustness** — `api/client.js` парсит JSON безопасно (фиксит «Unexpected token 'I'» из 500/HTML), убран `navigate('/coach')` (роута не было → пустой Layout с лого).
- **Подробности**: [[session-2026-05-26-wrestling-app-policy]], [[i18n-fallback-trap]].

**Why:** Артём — тренер wrestling клуба Constant Calgary Wrestling Club, приложение для управления клубом и мотивации спортсменов.
**How to apply:** nginx проксирует /api/ на :8001; `npm run build` деплоит в dist/; `sudo systemctl restart wrestling-api` для бэкенда.
