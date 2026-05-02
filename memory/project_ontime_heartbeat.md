---
name: OnTime Heartbeat & Time Policy
description: OnTime time-tracking model — geofence + explicit checkout + force-checkout + EOD 17:30 safety-net, минус 30 мин unpaid lunch (12:00-12:30 local).
type: project
originSessionId: d17635cc-9fb8-4333-ba35-356494af8a39
---
OnTime work_sessions закрываются по четырём причинам:
1. `checkout` — юзер сам (QR scan, `/api/me/checkout`, `/api/me/shift/end`).
2. `geofence_exit` — через `/api/heartbeat` (streak ≥3 outside-пингов подряд).
3. `force_checkout` — foreman/admin через `/api/projects/{pid}/force-checkout`.
4. `auto_checkout_eod` — **hard cutoff 17:30 local** (per-project timezone, default America/Edmonton). Добавлено 2026-04-17.

**EOD cutoff 17:30:** safety-net для случая «работник ушёл домой, забыл /checkout». `sweep_stale_sessions` закрывает любую открытую сессию, когда now_utc ≥ `_eod_cutoff_utc(started_at, tz)` = 17:30 local на дату старта сессии. Background asyncio task гоняет sweep каждые 60 сек (`SWEEP_INTERVAL_SECONDS=60`, @app.on_event('startup')).

**Unpaid lunch 12:00-12:30 local:** `_break_deduction_min(started, ended, tz)` вычисляет overlap по каждому локальному дню, `_close_session` вычитает из `duration_minutes`. Применяется на ВСЕХ путях закрытия.

**Контракт heartbeat** (`POST /api/heartbeat` {lat,lng}, каждые 60с пока вкладка foreground):
- Сервер находит открытую сессию юзера, считает `_haversine_m` до `project.lat/lng`.
- Порог — ровно `project.geofence_radius_m` (нет скрытых GPS-добавок).
- Внутри → обнуляем `outside_streak`, обновляем `last_inside_at`.
- Снаружи → `outside_streak += 1`; при `OUTSIDE_STREAK_LIMIT=3` подряд → `geofence_exit`, `ended_at = last_inside_at`.
- **Важно (после 2026-04-20):** удалили `geofence_exit_on_return` + `RETURN_FROM_BG_MIN` — один стрё́мный outside-пинг после сна телефона мог стирать часы. Теперь только streak.

**Silent-heartbeat алерт:** foreman-у Telegram раз на сессию при отсутствии heartbeat >`SILENT_HEARTBEAT_ALERT_HOURS=6` ч. Не закрывает сессию — это делает EOD cutoff. Алерт приходит с inline-клавиатурой из 2 кнопок:
- **✅ On site** (`callback_data=silent_ok:<sid>`) — foreman подтвердил, что работник на месте → сообщение ack-ается, сессия не трогается.
- **⛔ Force check-out** (`silent_out:<sid>`) → сообщение меняется на confirm-pair (**Yes, check out** / **Cancel**). Только Yes реально закроет сессию (`silent_out_yes`) с `end_reason=force_checkout`, `ended_at=now`, lunch-deduction применяется.

Хэндлеры в `tg_bot.py:cb_silent_alert` (`CallbackQueryHandler(pattern=r'^silent_')`). Авторизация: `sender.id == project.foreman_id` или `sender.role=='admin'`. Break-deduction вынесен в `backend/time_utils.py::break_deduction_min(started_iso, ended_iso, tz_name)` и используется ботом в `_close_session_force`. В `main.py` всё ещё своя локальная `_break_deduction_min` — логика идентична, при правках менять В ОБОИХ местах (или дорефакторить main.py на импорт из time_utils).

**Колонки work_sessions:** `end_reason`, `last_heartbeat_at/lat/lng`, `last_inside_at`, `outside_streak`, `silent_alert_sent_at`, `warned_at` (9ч notice), `break_deduction_min` (nullable sentinel для retro-migration).

**Константы:** `EOD_CUTOFF_HH=17`, `EOD_CUTOFF_MM=30`, `LUNCH_START=12:00`, `LUNCH_END=12:30`, `LONG_SHIFT_NOTICE_HOURS=9`, `SILENT_HEARTBEAT_ALERT_HOURS=6`, `OUTSIDE_STREAK_LIMIT=3`.

**Фронт:** `src/hooks/useHeartbeat.js` — висит в Shell, шлёт каждые 60с при наличии `api.myActiveSession()`. PWA геолокацию даёт ТОЛЬКО пока вкладка foreground — телефон в кармане ⇒ пингов нет, и это норма; счётчик времени при этом продолжает идти, т.к. серверное duration считается от `started_at` до закрытия.

**How to apply:** Правки учёта времени должны проходить через `_close_session`. Не писать UPDATE work_sessions напрямую для closing. Любой новый end_reason → добавить UI badge в `ProjectDetailPage.HoursTab`. Артём подтвердил 2026-04-17: жёсткий 17:30 cap и retroactive lunch deduction.
