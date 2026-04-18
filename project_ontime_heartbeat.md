---
name: OnTime Heartbeat & Time Policy
description: OnTime time-tracking model — geofence + explicit checkout + force-checkout + EOD 17:30 safety-net, минус 30 мин unpaid lunch (12:00-12:30 local).
type: project
originSessionId: d17635cc-9fb8-4333-ba35-356494af8a39
---
OnTime work_sessions закрываются по четырём причинам:
1. `checkout` — юзер сам (QR scan, `/api/me/checkout`, `/api/me/shift/end`).
2. `geofence_exit` / `geofence_exit_on_return` — через `/api/heartbeat`.
3. `force_checkout` — foreman/admin через `/api/projects/{pid}/force-checkout`.
4. `auto_checkout_eod` — **hard cutoff 17:30 local** (per-project timezone, default America/Edmonton). Добавлено 2026-04-17.

**EOD cutoff 17:30:** safety-net для случая «работник ушёл домой, забыл /checkout». `sweep_stale_sessions` закрывает любую открытую сессию, когда now_utc ≥ `_eod_cutoff_utc(started_at, tz)` = 17:30 local на дату старта сессии (или next day 17:30 если сессия стартовала после 17:30 local). Background asyncio task гоняет sweep каждые 60 сек (`SWEEP_INTERVAL_SECONDS=60`, @app.on_event('startup')), потому что иначе sweep срабатывал бы только на действиях юзеров.

**Unpaid lunch 12:00-12:30 local:** `_break_deduction_min(started, ended, tz)` вычисляет overlap по каждому локальному дню, `_close_session` вычитает это из `duration_minutes` и пишет в колонку `break_deduction_min`. Применяется на ВСЕХ путях закрытия. `_retro_break_deduction(conn)` на startup пробегает по closed-sessions с `break_deduction_min IS NULL` и обновляет их — миграция one-shot, guarded NULL-сентинелом. Brutto (`(ended-started)` минут) нигде не хранится отдельно, только `duration_minutes = gross - break_deduction_min`.

**Контракт heartbeat** (`POST /api/heartbeat` {lat,lng}, каждые 60с пока есть открытая сессия):
- Сервер находит открытую сессию юзера, считает `_haversine_m` до `project.lat/lng`.
- Порог — ровно `project.geofence_radius_m` (нет скрытых GPS-добавок; запас дрожи = шире радиус).
- Внутри → обнуляем `outside_streak`, обновляем `last_inside_at`.
- Снаружи: если gap >5 мин → `geofence_exit_on_return` (свернули app, вернулись вне зоны); иначе streak ≥3 подряд → `geofence_exit`. `ended_at = last_inside_at`.

**Silent-heartbeat алерт:** foreman-у Telegram раз на сессию при отсутствии heartbeat >3ч (`SILENT_HEARTBEAT_ALERT_HOURS`). Не закрывает сессию — это делает EOD cutoff.

**Колонки work_sessions:** `end_reason`, `last_heartbeat_at/lat/lng`, `last_inside_at`, `outside_streak`, `silent_alert_sent_at`, `warned_at` (9ч notice), `break_deduction_min` (nullable sentinel для retro-migration).

**Константы:** `EOD_CUTOFF_HH=17`, `EOD_CUTOFF_MM=30`, `LUNCH_START=12:00`, `LUNCH_END=12:30`, `LONG_SHIFT_NOTICE_HOURS=9`.

**Фронт:** `src/hooks/useHeartbeat.js` — висит в Shell, шлёт каждые 60с при наличии `api.myActiveSession()`. Toast на outside_warning/auto_checkout.

**How to apply:** Правки учёта времени должны проходить через `_close_session` — он держит и break deduction, и end_reason. Не писать UPDATE work_sessions напрямую для closing. Любой новый end_reason → добавить UI badge в `ProjectDetailPage.HoursTab`. PWA фонового GPS не даёт — on-return детект компромиссный; Capacitor не сделан. Артём подтвердил 2026-04-17: жёсткий 17:30 cap и retroactive lunch deduction.
