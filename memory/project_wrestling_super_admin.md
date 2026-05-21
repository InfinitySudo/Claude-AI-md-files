---
name: project-wrestling-super-admin
description: Cross-club super_admin view в wrestling app — Artem Borysiuk (id=17) + Art Papritskii (id=13)
metadata: 
  node_type: memory
  type: project
  originSessionId: c9d2b899-f272-4e25-b502-fa1e0f5284ca
---

## Кто super_admin

`users.is_super_admin BOOLEAN DEFAULT FALSE`. Сейчас TRUE для:
- **id=17** Artem Borysiuk (`borysiukartem1990@gmail.com`, coach, Constant)
- **id=13** Art (Papritskii Sr) (`constantcwc@gmail.com`, coach, Constant)

Флаг не меняет role или club_id — только открывает `/api/admin/*`. Назначается вручную через `UPDATE users SET is_super_admin = TRUE WHERE id = X`.

## Backend (`backend/main.py`)

Dependency `require_super_admin` гарантирует `user.is_super_admin === True`. Endpoints:
- `GET /api/admin/clubs` → все клубы + counts (coaches/athletes/guests/total) + `unassigned_users`.
- `GET /api/admin/clubs/{cid}/members` → полный members payload для конкретного клуба; `cid=0` = users без `club_id`.
- `GET /api/admin/all-members` → firehose (все клубы) + JOIN `club_name`/`club_city`. Используется в admin firehose view.
- `DELETE /api/admin/members/{uid}` → удаление; refuses self + другого super_admin (защита от self-lockout).

## Frontend

**Никакого отдельного `/admin` route или шилда.** Всё через ту же кнопку «People» на Coach Panel — `PeoplePill` в `src/pages/CoachDashboard.jsx`:
- Если `user.is_super_admin === true` → pill ВСЕГДА в admin-variant (даже до того как aggregate response пришёл). При тапе → `onOpen('all-clubs')` → `<ClubPeopleSheet adminClubId="all" />` тянет `/api/admin/all-members`.
- Иначе → обычный pill, sheet с `/api/members` (свой клуб).

`ClubPeopleSheet`:
- `adminClubId='all'` → admin firehose, club chip row под role chips динамически собирается из members payload (любой новый клуб появится chip'ом автоматически).
- `adminClubId=N` → конкретный клуб (used раньше из удалённой `/admin` route, оставлено как rescue).
- Trash icon рядом со строкой только для super_admin (не свой / не другого super_admin), invalidates `admin-all-members` / `admin-club-members` / `allMembers` / `admin-clubs-aggregate`.

**Both** `CoachDashboard` и `ClubPeopleSheet` используют `staleTime:0 + refetchOnMount:'always'` для `['me']` — иначе закэшированный pre-flag-flip `me` payload оставит pill в single-club режиме (Art попадался на это).

## Связано
- [[project_wrestling_v2]]
- [[project_wrestling_uww_scoreboard]]
- [[feedback_react_hooks_order]]
