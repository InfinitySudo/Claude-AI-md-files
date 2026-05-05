---
name: OnTime Check-in Time Policy
description: Hard-block раннего checkin'a + ±15min snap к shift_start/shift_end для чистых payroll-смен
type: feedback
originSessionId: 656b7c75-d454-4ed9-a10e-fd40c758b37e
---
TSA не разрешает рабочему делать checkin до того как сайт открыт, и не любит «9 часов 1 минута» в payroll. Реализовано в `/api/checkin` (`/root/ontime/backend/main.py`):

1. **Hard block before shift_start.** Если `projects.shift_start_time` задан и worker сканирует QR раньше этого local-времени — 403 «Site opens at HH:MM, please wait N min and scan again». Management (`_is_management`) пропускают для тестов/emergency.
2. **Snap to shift_start ±0..+15 min.** Сканы в окне [shift_start, shift_start+SNAP_WINDOW_MIN] записываются как `started_at = shift_start`. Опоздания >15 min — реальное время (видно в анти-обмане).
3. **Snap to shift_end ±15 min** (на checkout, force-checkout). `_resolve_eod_clock` теперь weekday-aware: Mon-Thu = +9h30m, Fri = +8h30m. EOD auto-checkout (`sweep_stale_sessions`) тоже это знает.

`SNAP_WINDOW_MIN = 15` константа на module-level.

**Why:** Артём сказал 2026-05-05 «не должно быть 9 часов 1 минута», и отдельно «работник не должен мочь сделать чек ин раньше 7am/8am, если site начинает работать с указанного времени при создании объекта». Без snap'а payroll был грязный; без блока работники могли «поджимать» бонус пунктуальности и накручивать минуты.

**How to apply:** Любая новая close-path для work_sessions должна снимать ту же snap-маску — иначе час между snap-checkin и raw-checkout даст некруглые числа. Пример: если кто-то добавит `/api/sessions/:id/close-manual`, обернуть end-time через `_snap_local_to_boundary(local_dt, hh, mm)`. Для start не делай snap до now() — это даст ретроактивный fake.
