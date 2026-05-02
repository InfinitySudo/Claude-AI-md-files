---
name: OnTime Invite Codes
description: Где хранятся коды приглашения для самостоятельной регистрации по ролям и какие точки в коде синхронизировать при добавлении новой роли
type: reference
originSessionId: 40266801-013a-4b79-9449-1d2920eae866
---
**Файл:** `/root/ontime/backend/.env.bot` (читается systemd-юнитом `ontime-api` через `EnvironmentFile=-`).

**Переменные (по состоянию на 2026-04-24):**
- `TSA_ADMIN_INVITE_CODE` (пустой = self-register закрыт) → role=admin
- `TSA_FOREMAN_INVITE_CODE`, `TSA_SERVICE_INVITE_CODE`, `TSA_DELIVERY_INVITE_CODE`
- `TSA_ACCOUNTANT_INVITE_CODE` (минует roster как admin; доступ к payroll/QB через `require_finance`)
- `TSA_PM_INVITE_CODE`, `TSA_VP_INVITE_CODE`, `TSA_DIRECTOR_INVITE_CODE`, `TSA_PURCHASING_INVITE_CODE`
- `TSA_MECHANIC_INVITE_CODE`
- `TSA_ESTIMATOR_INVITE_CODE`, `TSA_DIRECTOR_ESTIMATOR_INVITE_CODE`

**installer/helper** — код не нужен, регистрация валидируется по roster (админ заводит заранее).

**Why разные коды, а не один:** админ может выдать роль-код, не раскрывая admin-ключ. Кросс-подстановка блокирована: бэк проверяет код против конкретной переменной для выбранной position.

**How to apply:**
- При запросе "скажи код для X" — читать из `.env.bot`, не из памяти (коды ротируются).
- При ротации: правишь файл → `systemctl restart ontime-api`.
- **При добавлении новой роли** синхронизировать во ВСЕХ местах, иначе регистрация падает с "Invalid role" (так было с estimator 2026-04-24):
  - `backend/main.py`: `ROLES`, `POSITIONS`, `_position_to_role`, `INSTRUCTION_ROLES`, `GATED_POSITIONS`, `INVITE_CODES`, `NON_ROSTER_ROLES` (если office-роль), `MANAGEMENT_ROLES` (если нужен broad access)
  - `.env.bot`: новая `TSA_*_INVITE_CODE`
  - `src/pages/LoginPage.jsx`: три массива с ролями (отображение в select + gated-check + invite-code slot)
  - `src/lib/i18n.js`: переводы (en/ru/uk)
  - `src/lib/roles.js`: если роль должна видеть финансы/ревизии/документы
  - Пересобрать фронт (`npm run build`).
