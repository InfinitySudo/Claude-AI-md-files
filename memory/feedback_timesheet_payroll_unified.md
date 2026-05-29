---
name: feedback-timesheet-payroll-unified
description: Timesheet таб использует ТЕ ЖЕ правила что payroll _billable_hours_map — switched_project exception + 12h cap (унифицировано 2026-05-25)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3f969d3c-e080-450e-8ce9-fb152339bbc0
---

# Timesheet ↔ Payroll: единая логика

С 2026-05-25 endpoints `/api/timesheet/matrix` и `/api/timesheet/by-allocation`
используют ТЕ ЖЕ правила что payroll `_billable_hours_map`:

1. **report wins over session per (uid, day)** — если работник filed report
   где-либо, sessions на других проектах этого дня выбрасываются.
2. **switched_project exception** — session с `end_reason='switched_project'`
   засчитывается даже при наличии report на ДРУГОМ проекте, если на этом
   конкретном проекте report'a нет. Закрывает кейс transfer-сессий.
3. **MAX_BILLABLE_DAY_HOURS=12 cap** — если суммарно за день >12h по
   (uid, day), пропорционально scale все allocations. Защищает от дублирующих
   отчётов на разных проектах (физически невозможно работать 9h+9h).

**Why:** до фикса бухгалтер видел расхождения между Timesheet view и payroll
CSV export — например, Igor Chekmak 2026-03-18 показывал 18h в Timesheet
(сумма 9h+9h на двух проектах) vs 12h в payroll. Накопленно за 90 дней
Timesheet завышал на 11h (Igor +6h, Yaroslav +5h).

**How to apply:** trust payroll = trust Timesheet теперь идентичны. Если
будет новый похожий запрос от бухгалтера — сначала проверить что обновление
2026-05-25 применено (timesheet_matrix имеет блок с MAX_BILLABLE_DAY_HOURS
cap и check на end_reason == 'switched_project').

**Что НЕ переписано:**
- `/api/timesheet/anomalies` — это feature для нахождения проблем, не для
  расчёта totals; правила не нужны.
- Service / delivery hours в by-allocation — не подпадают под cap (их часы
  логически отдельны от project work).

Связано: [[feedback-billable-hours-dedup]] (исходная логика _billable_hours_map),
[[project-tsa-timesheet]] (matrix + by-allocation + anomalies).
