---
name: session-2026-05-26-wrestler-card-competitions
description: Wrestling app — карта борця + Competitions tab + Pro in-app rating + parental consent под-18 + Constant Wrestling ToS/Privacy. Commit 33bcc18.
metadata: 
  node_type: memory
  type: project
  originSessionId: be849f60-63be-4c16-b36d-b222e4c0a460
---

## Wrestling Performance Tracker — сессия 2026-05-26 (вечер, commit 33bcc18)

Второй большой проход за день — после `421573b` ([[session-2026-05-26-wrestling-app-policy]]).
13 файлов, +2053 / −42. Pushed: `InfinitySudo/Wrestling-Performance-Tracker@33bcc18`.

### Что вошло

**1. Constant Wrestling ToS / Privacy** (replacing generic platform terms)
- `DEFAULT_APP_POLICY` в `backend/main.py` теперь полный текст Terms of Service + Privacy Policy от Constant Calgary Wrestling Club (PIPEDA, Alberta governing law, contact `constantcwc@gmail.com`).
- Startup seed bump'ит `app_policies.version` если текст в коде изменился — все юзеры получат re-sign prompt.

**2. Карта борця (wrestler card)** (макет от Артёма с FloWrestling-style hero, [[session-2026-05-26-wrestling-app-policy]] добавил backend-стаб; теперь сделал full UI)
- Колонки: `hometown`, `wrestler_level`, `year_started_wrestling`, `bio`, `card_shared_at/approved_at/approved_by/rejected_reason`.
- ProfilePage hero «на свой лад»: rotating holo conic-gradient вокруг аватара (CSS keyframe `cw-spin-slow`), Constant **red-triangle brand chip** (вместо BETA из макета), country, ⚡ N-win streak badge, verified ✓ от тренера. Stats Overall W-L | Season W-L | Bonus-Wins %. Tabs Home / Results (in-app matches только).
- Workflow: атлет жмёт `Share to community` → row меняется на pending → coach видит в CoachDashboard inbox (фиолетовая секция 🪪) → approve/reject с reason. Reject — атлет может отредактировать и resubmit. Approved — карта public (видна всему сообществу).
- Endpoints: `GET /api/profile/{uid}/wrestler-card`, `GET /api/profile/{uid}/matches`, `POST /api/profile/share-card`, `GET /api/coach/card-reviews`, `POST /api/profile/{uid}/review-card`.

**3. Соревнования / Competitions** — отдельная club-scoped вкладка
- Новые таблицы `competitions` + `competition_signups`. Тренер постит выезд (name/date/location/age_groups/weight_categories/description/fee_usd/payment_link/payment_instructions); атлет выбирает свою возрастную+весовую категорию, читает инструкции оплаты, отправляет заявку → тренер approve participation + confirm payment. **Только участники клуба** видят roster, кто едет.
- Route `/competitions` + новый пункт в bottom-nav для athlete и coach (i18n: en `Competitions`, ru `Соревнования`). Иконка `Plane`.
- Endpoints: `/api/competitions` CRUD, `/signup`, `/signups`, `/signups/{sid}/review` (approve|reject|mark_paid), `/signups/me/mark-paid`.

**4. Pro league: in-app W/L rating**
- `GET /api/pro/rating?country=&weight_class=&age_group=` — агрегат wins/losses/win_pct/bonus_wins_pct/streak из `tournament_matches` где обе стороны = registered users + `winner_email` != NULL. Age group derived from DOB. Sort: wins ↓, win_pct ↓, BW% ↓.
- В `LigaProPage` под существующим manual-managed Pro списком — новая `InAppRatingCard` с фильтрами country/weight/age и top-50 leaderboard.

**5. Parental consent под-18**
- `users` новые поля: `parent_email/name/phone`, `parental_consent_token`, `parental_consent_at`, `needs_parental_consent`.
- `RegisterBody` теперь принимает `date_of_birth` + `parent_*`. Backend считает возраст; если athlete/guest <18 — обязательны parent_name+email; генерируем token, шлём email родителю с magic link `https://constantwrestling.cloud/parental-consent?token=…` (best-effort SMTP, fallback в журнал).
- LoginPage: новое поле `Date of birth *` для athlete/guest; если age<18 → автоматически показывается amber-блок «Parent / guardian (required)» с полями имени/email/phone.
- `/parental-consent` route + `ParentalConsentPage`: родитель видит имя ребёнка + полный текст app-policy + чекбокс «I confirm I am the parent/guardian of … and consent» + кнопка `Give consent` → POST `/api/parental-consent/{token}/accept`.
- `App.jsx` ConsentGate (внутри ProtectedRoute) опрашивает `/me` каждые 30s; если `needs_parental_consent === TRUE` — рендерит full-screen «Waiting for parent / guardian consent» с email и кнопкой Sign out. Как только родитель кликнул accept — следующий poll разблокирует UI автоматически.

### Follow-up commit 8c98ea7 — Club branding (logo upload)
- `clubs.logo_url` + `banner_url` columns; `POST /api/clubs/mine/logo` (multipart, PNG/JPG/WEBP/SVG, ≤4MB, only owner-coach или super-admin); `DELETE /api/clubs/mine/logo`.
- `Layout` header теперь рендерит `user.club.logo_url` (или fallback `/icon-192.png`) и `user.club.name` (или Constant Wrestling).
- `CoachDashboard` — секция «Club logo» под шапкой с превью + Upload/Replace + Remove.

### Что осталось / TODO
- Дать i18n-ключи на новые login.dob_required/parent_*/etc и `competitions_section.*` во все 10 языков (сейчас только EN/RU + английский fallback).
- Connecting `card_approved_at` к `members` list — отображать ✓ значок у тех, чья карта approved.
- Email SMTP — на prod `WPT_SMTP_*` не настроены, parental link сейчас попадает в `journalctl -u wrestling-api`. Когда Артём заведёт SMTP — заработает.
- Pro tab: full design (manual-managed Pro `LigaProPage` + новая InAppRating существуют параллельно; объединять или разводить — решение Артёма).

**Why:** Артём отправил длинный запрос (карта борця по макету Google Drive, новый формат вкладки Соревнования, парental consent для <18, тексты ToS/Privacy готовые). Этот сеанс закрыл всё одним коммитом.
**How to apply:** перед правкой Wrestling — прочитать [[project-wrestling-v2]] + этот файл + [[session-2026-05-26-wrestling-app-policy]] подряд (это два разных коммита одного дня).
