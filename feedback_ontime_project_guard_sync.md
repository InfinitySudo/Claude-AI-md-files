---
name: OnTime Project/Reports Guard Sync
description: GET /api/projects/{pid} installer-guard и POST /api/reports crew-guard ОБЯЗАНЫ принимать одинаковую crew-evidence (pinned ∪ helper ∪ recent QR)
type: feedback
originSessionId: b6d40f12-7ceb-47ab-97ab-a62197ce1971
---
GET `/api/projects/{pid}` (для `role='installer'`) и POST `/api/reports` должны принимать одинаковые источники доказательства членства в крю: `project_installers` ∪ активный `project_helpers` ∪ work_sessions за 14 дней. Если расходятся — installer может сабмитить отчёт (POST мягче), но не загрузить страницу проекта чтобы увидеть materials → форма показывает «No materials».

**Why:** 2026-05-06 Артём пожаловался: на Sage Hill 600 и MG84 Bldg 20 рабочие не видят материалы при заполнении отчёта. Причина — POST /api/reports с 2026-04-29 принимает 14d-сессии и авто-пинит, а GET /api/projects/{pid} оставался на старом узком guard'е (только pinned/helpers). Orphan-проекты после legacy-импорта 2026-04-17 + edits проектов (`PATCH /api/projects` стирает `project_installers` если сабмитят installer_ids=[]) — крю «реально работает», но `project_installers` пустой.

**How to apply:**
- При любом редактировании любого из этих двух guard'ов — править оба синхронно.
- Если страница проекта/деталей проекта показывает что-то завязанное на membership (BOM, photos, messages) — гонять то же правило.
- Backfill команда (используй на orphan-проектах: `status IN ('active','in_progress','overdue','planned')`, `project_installers` пустой/маленький, есть свежие reports/sessions):
  ```sql
  INSERT OR IGNORE INTO project_installers (project_id, installer_id, added_by)
  SELECT DISTINCT c.project_id, c.user_id, c.user_id FROM (
    SELECT ws.project_id, ws.user_id FROM work_sessions ws
      JOIN users u ON u.id=ws.user_id JOIN projects p ON p.id=ws.project_id
      WHERE u.role='installer' AND p.archived=0
        AND p.status IN ('active','in_progress','overdue','planned')
        AND substr(ws.started_at,1,10) >= date('now','-30 days')
    UNION
    SELECT dr.project_id, dr.user_id FROM daily_reports dr
      JOIN users u ON u.id=dr.user_id JOIN projects p ON p.id=dr.project_id
      WHERE u.role='installer' AND p.archived=0
        AND p.status IN ('active','in_progress','overdue','planned')
        AND dr.report_date >= date('now','-30 days')
  ) c;
  ```
- Backup перед backfill: `cp tsa.db tsa.db.bak-before-pin-backfill-$(date +%Y%m%d-%H%M%S)`.
