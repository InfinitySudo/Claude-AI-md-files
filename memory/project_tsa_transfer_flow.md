---
name: OnTime Worker Transfer Flow
description: Перемещение работника между active projects — три пути: pull-now (one-tap, foreman target), transfer-request (worker сам сдаёт отчёт), и оригинальный 409-блок если caller не имеет прав
type: project
originSessionId: 2698e6df-f89c-4d5c-ae55-ba7c1be6f1d9
---

**С 2026-04-27:** `pending_transfers` flow вместо старого каскадного `_force_detach_worker_company_wide` (он остался в коде, но НЕ вызывается из add-эндпоинтов).

**С 2026-04-29:** добавлен **pull-now** как third path — one-tap перевод инициирует foreman to-проекта (или management). Backfill 43 записей в `project_installers` из daily_reports + auto-pin hook в POST /api/reports.

**Why блокировки:** Старая каскадная логика сносила рабочих из crew без следа. Igor K: «утренние списки к вечеру разваливаются». Часы и материалы должны оставаться привязаны к bldg где был чекин.

**Why pull-now:** Артём: «foreman должен контролировать процесс, не ждать пока worker сам соберётся». Решение: переводить можно сразу, но открытая QR-сессия закрывается → часы синтезируются в `daily_reports.kind='auto_transfer'` → foreman A получает push-нотификацию и может править отчёт до 23:59.

## Три пути перемещения

### 1. Pull-now (новый, 2026-04-29)
- `POST /api/workers/{uid}/pull-now` body `{ to_project_id, from_project_id? }`
- Auth: foreman to-проекта или management.
- Атомарно: create/upsert pending_transfer (auto_pulled=1) → `_close_open_sessions_on_transfer` (закрывает open work_session, end_reason='transfer') → синтезирует `daily_reports` (kind='auto_transfer', hours = `_session_hours_authoritative`) → `_apply_pending_transfer` → notify worker + foreman A.
- Поле `can_pull_now: bool` приходит в 409 response от add_helper/add_installer/PATCH projects — фронт сам определяет показывать ли кнопку.

### 2. Transfer-request (классический, 2026-04-27)
- `POST /api/workers/{uid}/transfer-request` — для случаев когда foreman A инициирует, или нужны custom часы/материалы (worker сам заполняет отчёт).
- Worker получает TG + bell с deeplink на `/daily-reports/new?project_id=<from>`.
- Когда landing report делается — `_apply_pending_transfer` срабатывает в POST /api/reports handler.

### 3. 409 transfer_required (block)
- Если caller не foreman/mgmt to-проекта — 409 без `can_pull_now`. Просят админа.

## How to apply при изменениях

- `_other_active_membership` — single source of truth для «worker на чужом active проекте».
- `_can_pull_now(conn, user, project)` — проверка прав на pull-now (foreman of project + mgmt).
- 409 ответ всегда содержит: `code='transfer_required'`, `conflicts: [{project_id, name, slot}]`, `can_pull_now: bool`, `worker_id?`.
- Stale-nudge: `nudge_stale_transfers` (60s sweep) — пингует через 1ч если transfer-request stuck.
- Cancel: `DELETE /api/workers/{uid}/transfer-request` (foreman/admin/worker сам).

## Frontend

- `AddPersonModal` (ProjectDetailPage) — при 409 показывает inline conflict-block: список chuжих проектов + кнопка «Pull now» если `can_pull_now`. При single conflict from_project_id implicit, при multiple — нужно явно (пока не реализовано в UI).
- `TransferModal` — отдельный для классического transfer-request.
- Banner в `InstallerHomePage` если есть `myPendingTransfer`.
- `api.workers.pullNow(uid, to_pid, from_pid?)` — клиент.

## i18n keys (en/ru/uk)

`transfer_worker`, `transfer_requested`, `transfer_explainer`, `request_transfer`, `awaiting_report_to`, `to_project`, `from`, `pending_transfer_banner`, `submit_report_now`, `cancel_transfer`, **`pull_now`, `pull_now_explainer`, `worker_on_other_project`, `hours_auto_closed`, `installer`, `helper`** (последние 6 — 2026-04-29).

## Schema

- `daily_reports.kind` TEXT DEFAULT 'eod' — values: `'eod' | 'transfer' | 'auto_transfer'`.
- `pending_transfers` с unique active index на user_id (один pending на работника).
- `pending_transfers.auto_pulled` INTEGER NOT NULL DEFAULT 0 (2026-04-29) — отделяет one-tap pull от классического request.
- `work_sessions.end_reason='transfer'` — закрытая pull-now'ом сессия.
