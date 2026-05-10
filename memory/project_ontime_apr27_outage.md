---
name: OnTime 2026-04-27 Domain Outage Compensation
description: 27 апреля 2026 утром был отключён домен ontime.management → check-in не работал; всем 26 рабочим вручную проставили 9.0h
type: project
originSessionId: b3cbd579-83db-48e9-85ab-677bcc6f8cfe
---
2026-04-27 (понедельник) утром домен ontime.management был отключён, рабочие не смогли сделать QR check-in вовремя. Артём с Claude проставили всем 26 пострадавшим рабочим `hours = 9.0` (full Mon workday) через manual override как компенсацию простоя. Сессии в этот день стартовали 15:25-16:04 UTC (9:25-10:04 Calgary, опоздание из-за outage), фактически отработали ~6-7.5h.

**Why:** компенсация за простой по причине системного сбоя на стороне OnTime, а не работника.

**How to apply:**
- Эти 26 reports НЕ трогать. При любом аудите часов / payroll они выглядят как overcounting (stored 9.0 vs computed 5.9-8.1) — это не баг, а решение.
- В будущем при подобных outage'ах применять ту же схему: ставить полный day-base через PATCH /api/reports/{rid}.
- При backfill'ах фильтровать диапазон `report_date BETWEEN '2026-04-01' AND '2026-05-31'` исключая 2026-04-27 если есть сомнения.
