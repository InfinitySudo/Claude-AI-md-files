---
name: session-2026-05-19-wrestling-coach-toolkit
description: "Wrestling app — club policy, groups, password reset, live sparring scoring, EN/RU/PL i18n, birthday reminder daemon (commit ddeee40)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6bb3f02b-ebb6-4591-8701-65bd0ef586ad
---

# Wrestling-Performance-Tracker — Coach Toolkit (2026-05-19)

Commit `ddeee40` "Coach toolkit: club policy, groups, password reset, live sparring + i18n" (+2213/-133 across 19 files).

## Backend (PostgreSQL migrations are additive)
- `club_policies` + `policy_acceptances` — canonical Constant policy seeded on boot. Coach: `PUT /api/clubs/mine/policy` (bumps version if content changed → invalidates acceptances). Athletes sign at register and via `POST /api/profile/accept-policy`. Public read: `GET /api/clubs/policy?invite_code=...` (so register-form can show text before login).
- `user_groups` + `users.group_id` — CRUD via `/api/groups` and `PATCH /api/users/{uid}/group`. `/api/members` and `/api/rankings` JOIN `user_groups` to expose `group_name`. `users.preferred_language` added.
- `password_resets` — `POST /api/auth/reset-request` always 200; tokens are `uuid4().hex + uuid4().hex[:16]`, TTL 1h, one-shot. `_send_reset_email()` uses `WPT_SMTP_*` env; missing creds → token logged to journald and link goes nowhere unless admin reads logs.
- `sparring_scores` — `POST /api/tournaments/{tid}/score` (coach-only, club-scoped). `GET /api/tournaments/{tid}/scores`. Folded into `/api/rankings.sparring_pts` and `/api/profile.points_sparring`.
- `birthday_reminders` (user_id, year) UNIQUE — daemon thread inside FastAPI loops every 30 min, fires `_run_birthday_sweep()` once when 14:00–15:00 UTC and date hasn't been processed. Sweep pings athlete + every coach in the club via `_wp_notify`. Manual trigger: `POST /api/admin/birthday-sweep` (admin-only).

## Frontend
- **i18n**: `src/i18n/{index.js,en.json,ru.json,pl.json}` via react-i18next; `LanguageSwitcher` in login footer, persisted to `localStorage.wpt_lang`. Layout nav labels translate via `nav.<key>` keys.
- **LoginPage**: forgot-password (`reset_request` → `reset_confirm` via `?reset_token=` URL); mailto:constantcwc@gmail.com + Telegram link as contact chips; policy modal w/ checkbox required for athlete/guest, auto-fetches policy by `invite_code` on entry.
- **PolicyPage** (`/policy`): coach edits in textarea (bumps version), athlete sees acceptance banner if `requires_acceptance`.
- **MembersPage**: groups manage-panel + chip-row filter + sort (group/name/points) + inline `<select>` to assign. `total_points` now live-computed in backend (norms+analysis+attendance+sparring), supersedes `total_points_monthly`.
- **NormsPage**: branches by role. Coach: tabs (Matrix, Create, History); Matrix is athletes × unique norm-names table. Athlete: original pending/submitted/confirmed/rejected layout.
- **CoachDashboard**: norms section collapsed to slim card linking to `/norms` (old big inline UI wrapped in `display:none` div for anchor links); new `RankingsWidget` shows top-5 with breakdown.
- **TournamentsPage**: `SparringLiveScoring` card under matches. Polls `api.sparring.list(tid)` every 5s. Quick buttons +1/+2/+3/+5/-1 + custom ±N + optional note; running totals per athlete; coach-only delete on history strip.

## Files (where to look)
- Backend: `backend/main.py` (all endpoints + migrations in single file). DEFAULT_CLUB_POLICY constant ≈ line 130.
- Frontend new: `src/i18n/`, `src/components/LanguageSwitcher.jsx`, `src/pages/PolicyPage.jsx`.
- Frontend modified: `LoginPage.jsx`, `MembersPage.jsx`, `NormsPage.jsx`, `CoachDashboard.jsx`, `TournamentsPage.jsx`, `App.jsx`, `Layout.jsx`, `api/client.js`, `main.jsx`.
- CLAUDE.md fixed: lied about SQLite + generic unit name. Correct: `wrestling-api.service` + PostgreSQL.

## Known gaps to revisit
- SMTP env-vars (`WPT_SMTP_HOST/PORT/USER/PASS/FROM`) not set on prod — reset links currently print to journald only.
- Policy modal only triggers when invite_code already filled (≥4 chars) — empty-invite athletes need to enter code first; acceptable for now.
- Old norms UI is wrapped in `display:none` rather than deleted — once we confirm no deep-links break, drop the legacy block.
- Geolocation / "player map" / live-points-in-private-sparrings beyond simple tournaments not implemented this round.

**Why:** Артём попросил функционал, который болит на тренировке — управление группами, политика клуба и подпись, забытый пароль, живые баллы во время спарринга, многоязычность и напоминание о ДР.
**How to apply:** при изменениях в этой части сверяйся с `project_wrestling_v2.md`; политика/группы/scores интегрированы в leaderboard и members — любая правка `/api/rankings` или `/api/members` должна сохранять эти поля.
