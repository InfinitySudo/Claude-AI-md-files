---
name: project-wrestling-account-deletion
description: "Wrestling app: self-service удаление аккаунта (Apple 5.1.1v). DELETE /api/me?confirm=true анонимизирует users-строку (не hard-delete). UI — Danger Zone в ProfilePage. Готово на web (commit 3972f62), в iOS-сборку войдёт при пересабмите."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9924a9cb-baa9-4aa6-aeee-d2beb8128b55
---

Добавлено 2026-05-29 (commit `3972f62`) — проактивно, на случай реджекта v1.0 по **App Store Guideline 5.1.1(v)** (приложение с регистрацией обязано давать удалить аккаунт прямо в приложении). До этого фичи не было — частая причина реджекта.

**Backend** (`backend/main.py`): `DELETE /api/me?confirm=true` (auth required).
- Удаляет личные записи по email: attendance, norm_standards, training_analysis, tournament_participants.
- **Анонимизирует** строку `users` (НЕ hard-DELETE — чтобы не упасть на FK из sparring_scores/sessions и пр.): email → `deleted_{id}_{rnd}@deleted.invalid`, password_hash → случайный (вход невозможен), стирает все PII-колонки (full_name='Deleted user', photo/соцсети/контакты/parent_*/dob/bio/...).
- `confirm=true` обязателен, иначе 400.

**Frontend** (`src/pages/ProfilePage.jsx`): компонент `DangerZoneCard` — красная кнопка «Delete account» → inline-подтверждение → `api.deleteAccount()` (`src/api/client.js`: `DELETE '/me?confirm=true'`) → `localStorage.removeItem('wpt_token')` + `window.location.href='/login'`. i18n через `t(key, default)` (см. [[feedback-i18n-fallback-trap]]).

**Проверено E2E:** login → DELETE → PII очищены, email=tombstone → повторный вход старыми кредами 401.

**Статус:** live на web (dist gitignored, билд задеплоен, `wrestling-api` рестартнут). **В iOS-приложение войдёт только при следующей Capacitor-сборке + пересабмите** — текущий build 79860157 (submission acf3e653) его НЕ содержит. См. [[project-session-2026-05-27-wrestling-v1-0-submit]].
