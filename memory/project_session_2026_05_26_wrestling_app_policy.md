---
name: session-2026-05-26-wrestling-app-policy
description: "Wrestling app — большой проход 2026-05-26 — app-policy, geo-signup, camp admin-verify, roll-call, extra-tasks, sparring i18n, leagues tours select, analysis re-submit, norm finalize. Commit 421573b."
metadata: 
  node_type: memory
  type: project
  originSessionId: be849f60-63be-4c16-b36d-b222e4c0a460
---

## Wrestling Performance Tracker — сессия 2026-05-26 (commit 421573b)

Большой проход по requested списку Артёма. 18 файлов, +1607 / −106.
Pushed: `InfinitySudo/Wrestling-Performance-Tracker@421573b` (main).

### Что вошло

**Registration + policies** (см. [[project-wrestling-v2]])
- App-wide policy: новая таблица `app_policies`, эндпойнты `/api/app-policy` (public read) + `/api/admin/app-policy` (super-admin update). Default text сидится при первом старте.
- Каждый при регистрации, **включая тренера**, подписывает app-policy (`app_policy_accepted` обязательно — bypass `if (form.role === 'coach') payload.policy_accepted = true` остался только для club-policy, но новый app-policy чекбокс обязателен для всех).
- Club-policy больше **не сидится** автоматически в новые клубы (старая авто-выдача Constant-текста убрана). Новый клуб — пустой policy, тренер пишет сам через `/policy`.
- При регистрации обязательны `country` + `region` (province/state). `timezone` авто-определяется через `Intl.DateTimeFormat().resolvedOptions().timeZone`. Кнопка 📍 «use my location» (Nominatim reverse-geocode) заполняет country/region/club_city.

**Camps** (см. [[project-wrestling-camp-payment]])
- При создании кемпа обязательны `contact_phone`, `contact_email`, `country`, `region`; опционально `socials_url`.
- Новое поле `admin_status` ('pending_admin' | 'approved' | 'rejected'). Кемп виден только создателю + супер-админу до approve; после approve — публичный.
- `POST /api/admin/camps/{id}/verify` — супер-админ approve/reject с причиной, push-уведомление создателю.
- `GET /api/camps?country=&region=` + `GET /api/camps/countries` — фильтр в UI.
- В UI: бейдж PENDING/REJECTED, ✓/✕ кнопки для супер-админа.

**Sessions** ([[project-wrestling-v2]])
- Убран жёсткий триплет Kids/Junior/Senior в форме создания тренировки — теперь либо "All members", либо группы тренера (через Manage Groups / `user_groups`).
- Новые таблицы: `session_extra_tasks`, `session_signups`, `session_extra_task_confirms`.
- Backend: signup/signoff, listSignups, rollCall (idempotent — отметил кто пришёл, начислил attendance points, остальным сброс), createExtra/deleteExtra/confirmExtra/unconfirmExtra (extra-confirm gated на `present=true`).
- SessionPage переписан: атлет видит Sign-up/Cancel и свой attendance-статус; тренер видит roll-call с чекбоксами + настройкой attendance points + ниже Bonus tasks (create + per-present pill confirm).

**Sparrings**
- i18n-ключи `sparring_section.format_*`, `bracket_single_elim`, `matches_round_robin`, `regenerate_confirm`, `min_participants`, `press_generate` добавлены во **все 10** языков (en/ru/uk/pl/ar/fa/zh/ja/pa/es).
- TournamentsPage использует `t()` вместо хардкода RU.

**Leagues** ([[project-wrestling-v2]])
- "Number of tours" → `<select>` 1..5 в Create и Edit карточках (было `<input type="number" 1..20>`).

**Analysis**
- `UNIQUE(session_id, athlete_email)` — один analysis per training per athlete, дубли невозможны.
- POST /api/analysis теперь upsert: при существующей строке со статусом `submitted` или `rejected` обновляет содержимое; при `reviewed` — 409.
- Reject path: coach передаёт `coach_review` с префиксом `REJECT:` ИЛИ `points_awarded < 0` → status='rejected', ученик может отредактировать и переотправить.

**Norms**
- `POST /api/norms/finalize` — батч-финализация события: лидер за каждое упражнение = max_points, –1 за каждое следующее место (минимум 0), плюс overall-ranking bonus сохраняется синтетической строкой `🏅 Overall ranking bonus`.

**Client**
- `request()` в `src/api/client.js` теперь читает body как `text()` сначала, парсит JSON безопасно — фиксит «Unexpected token 'I'...» из 500/HTML ответов.
- LoginPage: убран `navigate('/coach')` — route не существовал, итог: пустой Layout с лого ([[project-session-2026-05-19-wrestling-coach-toolkit]] контекст).
- Новые API helpers: `api.appPolicy.{get,update}`, `api.camps.{adminVerify,countries}`, `api.sessions.{listExtras,createExtra,deleteExtra,confirmExtra,unconfirmExtra,signup,signoff,listSignups,rollCall}`, `api.norms.finalize`.

**Migrations (все idempotent)**
- `clubs.{country,region,timezone}`
- `users.{country,region,timezone,app_policy_accepted_version}`
- `app_policies` table
- `camps.{contact_phone,contact_email,socials_url,country,region,admin_status}` default 'pending_admin'
- `session_extra_tasks`, `session_signups`, `session_extra_task_confirms`
- `training_sessions.group_id`
- `training_analysis.{status,coach_comment,points_awarded,edited_at}`
- `CREATE UNIQUE INDEX uniq_analysis_session_user ON training_analysis(session_id, athlete_email) WHERE session_id IS NOT NULL`

### Verified

Прогнал Python Playwright против live https://constantwrestling.cloud:
1. ✅ /login register показывает Country/Region/Timezone + 📍 + Platform Terms блок
2. ✅ "Read platform terms" модал с правильным текстом
3. ✅ Submit без app-policy → toast 'Please accept the platform policy'
4. ✅ /camps Create — все 5 обязательных полей видны
5. ✅ /leagues Number of tours → select ['1 tour'..'5 tours']
6. ✅ /session/{id} → Roll-call + Bonus tasks, 0 console errors
7. ✅ /tournaments format buttons localised EN; RU-режим тоже работает

Скриншоты `/tmp/verify_shots/0[1-8]_*.png`.

### Что осталось

- Backend для **task 12 (norm batch finalize)** есть, UI для тренера (выбрать норм-event и нажать Finalize) — TODO. Сейчас зовётся через `api.norms.finalize([ids])` напрямую.
- Country filter в /camps не виден пока нет approved-camps со страной в БД — это правильное поведение.
- TODO: Edit-form для extra-tasks при создании тренировки в CoachDashboard (сейчас extra-tasks добавляются только на странице сессии, не сразу при создании). Скоуп задачи #5 покрыт минимально.

**Why:** Артём прислал длинный список фич и багов одним сообщением; этот checkpoint фиксирует scope и место в коде, чтобы при следующем заходе быстро вернуться.

**How to apply:** перед правкой Wrestling — прочитать этот файл, затем [[project-wrestling-v2]] для общего контекста. Любые правки реестра ролей / policy / camps идут через эту схему, не через старую club-only policy.
