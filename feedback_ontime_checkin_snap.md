---
name: OnTime Check-in Time Policy
description: Early scans clamped to shift_start + ±15min snap к shift_end для чистых 9h/8h смен
type: feedback
originSessionId: 656b7c75-d454-4ed9-a10e-fd40c758b37e
---
TSA не любит «9 часов 1 минута» в payroll. Реализовано в `/api/checkin` (`/root/ontime/backend/main.py`):

1. **Early scans clamped to shift_start (с 2026-05-06).** Если `projects.shift_start_time` задан и worker сканирует QR ДО этого времени — checkin принимается, но `started_at` зажимается в shift_start. Раньше (2026-04-30 → 2026-05-06) это был 403 hard-block, но Артём отменил («работники должны мочь скан до 7am/8am, время идёт с шифт-старта»). Управленцы шли по тем же правилам (без bypass'а).
2. **Snap to shift_start ±0..+15 min.** Сканы в окне [shift_start, shift_start+SNAP_WINDOW_MIN] → `started_at = shift_start`. Опоздания >15 min — реальное время (видно в анти-обмане).
3. **Snap to shift_end ±15 min** (на checkout, force-checkout). `_resolve_eod_clock` weekday-aware: Mon-Thu = +9h30m, Fri = +8h30m. EOD auto-checkout (`sweep_stale_sessions`) тоже это знает.

`SNAP_WINDOW_MIN = 15` константа на module-level.

**Why:** Артём 2026-05-05 «не должно быть 9 часов 1 минута» (snap). 2026-05-06: hard-block раннего скана отменён — «работники не должны быть отшиты от QR'a в 6:45 если шифт в 7:00; время всё равно начнёт идти с 7:00». В сумме: ровно 9h Mon-Thu / 8h Fri вне зависимости от того когда крю прошло через ворота.

**How to apply:** Любая новая close-path для work_sessions должна снимать ту же snap-маску — иначе час между snap-checkin и raw-checkout даст некруглые числа. Пример: если кто-то добавит `/api/sessions/:id/close-manual`, обернуть end-time через `_snap_local_to_boundary(local_dt, hh, mm)`. Для start не делай snap до now() — это даст ретроактивный fake.
