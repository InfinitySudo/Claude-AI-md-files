---
name: OnTime Lifts + Refuel Tracking
description: Delivery driver fuel-tracking feature — 11 lifts catalog, per-refuel log with photo+cost+engine hours, monthly consumption report
type: project
originSessionId: e468c151-0562-45d4-a98c-b5ca8d047a67
---
Добавлено 2026-04-23 по запросу Артёма: David Ivanets совмещает доставку
материалов и заправку лифтов → одна роль `delivery`, отдельная
sub-сущность refuel (не смешивать с `shift_stops`).

## Схема (tsa.db)
- `lifts(id, company_id, name, model, serial, fuel_type, tank_liters,
  status, notes, archived, created_at)` — unique (company_id, name).
- `lift_refuels(id, lift_id, user_id, work_session_id, liters,
  engine_hours, cost_cad, receipt_photo, notes, created_at)`.

## Seed (company_id=1) — 11 единиц
SkyJack S65-01..S65-05, S65-07 (6 шт.); Genie S65-06, S85-01, S85-02,
S85-03 (4 шт.); Telehandler Zoom-Boom (1 шт.). Все `fuel_type=diesel`.

## API (main.py `# ── Routes: Lifts catalog + refuels ──`)
- `GET /api/lifts` — any authenticated user. `?include_archived=1`.
- `POST/PATCH /api/lifts[/{id}]` — `require_management`.
- `DELETE /api/lifts/{id}` — admin, **soft-delete** если есть refuels
  (archived=1), иначе hard delete.
- `POST /api/me/shift/refuels` — любой user; `work_session_id`
  подхватывается автоматически если смена открыта (может быть NULL).
- `GET/DELETE /api/me/shift/refuels[/{id}]` — свои записи.
- `POST /api/refuels/{id}/photo` — загрузка чека (uploader or management).
  Файлы в `uploads/refuels/<uuid>.jpg`, 1600×1600 JPEG q82.
- `GET /api/lifts/{id}/refuels?days=180` — история по лифту.
- `GET /api/lifts/consumption?month=YYYY-MM` — management-only; группировка
  по лифту: total_liters, total_cost_cad, refuels_count,
  latest_engine_hours. Default month = текущий UTC.
- `DELETE /api/refuels/{id}` — management audit-fix.

## PWA
- `src/pages/ShiftPage.jsx`: вторая кнопка "⛽ Refuel lift", модалка
  `AddRefuelModal` c dropdown из `/api/lifts`, полями liters (required),
  engine_hours, cost_cad, photo (`capture="environment"`), notes.
  Блок "Recent refuels" (30 дней) рядом с "Today's stops".
- `src/pages/LiftsPage.jsx` (новая) — admin CRUD + month-picker отчёт
  расхода + per-lift history modal. Route `/lifts`, nav-кнопка видна
  для `hasFinanceView(me)`.
- `api.lifts.{list,create,update,remove,refuels,consumption}` +
  `api.shiftAddRefuel / shiftRefuels / shiftDeleteRefuel /
  refuelUploadPhoto` в `src/api/client.js`.
- i18n для EN/RU/UK: refuel_lift, add_refuel, recent_refuels, lift,
  liters, engine_hours, cost_cad, receipt_photo, pick_lift, lifts,
  consumption_month.

## Дизайн-решение: одна роль, разные sub-задачи
Рассматривали вариант отдельной роли `refueller`, но:
- David — один физический человек, один аккаунт — не нужно плодить
  invite codes
- Задачи по семантике обе — "field stops во время смены"
- НО данные разные: customer+address у доставки vs lift+liters+cost+photo
  у заправки → отдельная сущность, не расширение `shift_stops`

Это упрощает запросы расхода: `SELECT lift_id, SUM(liters) ... GROUP BY
lift_id` без фильтра по `type`.

**Why:** правильный отчёт расхода по лифтам за месяц — ключевой KPI
(Артём упоминал "за месяц расход 350L по SkyJack S66-01"). Плоский
список stops этого не даёт без костылей.

**How to apply:** при добавлении похожих видов field-работ (доставка
инструмента, тех. осмотр, погрузка) — сразу заводить отдельную сущность,
не разбухать `shift_stops` колонками.

## Mechanic роль (добавлено 2026-04-23)

Новая роль `mechanic` для отдельного человека (НЕ David — David остаётся
delivery с правом заправлять; mechanic делает ТО).

**Invite code:** `Mechanic-2026-VVKJKR` в `.env.bot` → TSA_MECHANIC_INVITE_CODE.

**Добавлено в backend:**
- `LIFT_MANAGER_ROLES = {admin, pm, vp_construction, director,
  purchasing_manager, mechanic}` — новая группа отдельно от MANAGEMENT
- `_is_lift_manager()` + `require_lift_manager()` FastAPI dependency
- `mechanic` в ROLES / POSITIONS / GATED_POSITIONS / NON_ROSTER_ROLES
- `_position_to_role('mechanic')` → `'mechanic'` (не installer)
- Схема `lifts`: `service_interval_hours` (def 500), `last_service_hours`,
  `last_service_date`, `monthly_liter_alert`
- Таблица `lift_service_log` — audit ТО
- `GET /api/lifts/maintenance` — график ТО (любой user, read-only)
- `POST /api/lifts/{id}/service` — логирование ТО (lift_manager); routine
  и repair сбрасывают maintenance clock, inspection — нет
- `GET /api/lifts/{id}/service-log` — любой user
- `DELETE /api/lifts/service-log/{sid}` — lift_manager

**Permission matrix (проверено smoke-тестами 2026-04-23):**
| Действие                       | delivery | installer | mechanic | admin |
|--------------------------------|---------|-----------|----------|-------|
| GET /api/lifts                 | ✅      | ✅        | ✅       | ✅    |
| GET maintenance + consumption  | ✅      | ✅        | ✅       | ✅    |
| GET service-log                | ✅      | ✅        | ✅       | ✅    |
| POST /api/lifts (create)       | ❌ 403  | ❌ 403    | ✅       | ✅    |
| PATCH /api/lifts/{id}          | ❌      | ❌        | ✅       | ✅    |
| POST /api/lifts/{id}/service   | ❌      | ❌        | ✅       | ✅    |
| DELETE /api/lifts/{id}         | ❌      | ❌        | ❌       | ✅    |
| POST shift/refuels (заправка)  | ✅      | ❌        | ✅*      | ✅*   |
| POST shift/start (открыть смену)| ✅      | N/A†      | ❌       | N/A†  |

\* lift_manager может ради correction/audit; основной flow — delivery.
† installer/admin не используют shift-mode, checkin по QR или не нужно.

**Frontend:**
- `src/lib/roles.js`: `canManageLifts(me)` — для мутаций; `canViewLifts(me)`
  — для nav-кнопки (включает delivery/service read-only)
- `App.jsx` nav: кнопка `⛽ Lifts` показывается для canViewLifts
- `LiftsPage.jsx` принимает `me` пропом, скрывает Add/Edit/Delete/Service
  кнопки если `!canWrite`
- Mechanic лэндит на `/` → LiftsPage (не ProjectsPage)
- TG-bot welcome распознаёт `position==mechanic` и говорит "use PWA"

**Обязанности не пересекаются:**
- David (delivery): заправляет, вводит литры/moto hours/чек; НЕ делает ТО
- Mechanic: видит maintenance schedule с David'овыми показаниями, делает
  ТО и логирует → clock обнуляется; НЕ заправляет (разве что correction)
- Admin/management: полный доступ, видит всё; только admin может DELETE
