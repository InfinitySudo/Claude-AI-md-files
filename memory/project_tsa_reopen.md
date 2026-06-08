---
name: project_tsa_reopen
description: OnTime — реактивация завершённых (done) проектов без 48h-окна
metadata: 
  node_type: memory
  type: project
  originSessionId: f95a45b7-5136-481f-b75d-874bf3fb389e
---

OnTime: завершённый проект можно вернуть в активные.

- **POST /api/projects/{pid}/reopen** (require_management) — без ограничения 48 ч: удаляет project_scores, обнуляет closed_at/actual_hours/prev_status, ставит status='active'. Очки начислятся заново при следующем закрытии.
- Старый **DELETE /api/projects/{pid}/complete** (undo_complete) остаётся: только admin и только 48 ч, восстанавливает prev_status.
- UI: ProjectDetailPage — кнопка «Сделать активным» (reopen_project) для менеджмента на любом done-проекте; рядом с Complete.
- i18n EN/RU: reopen_project, reopen_confirm.

Commit d88db62 (2026-06-05). MG84 Bldg 14 (id 63) реактивирован вручную тем же путём (бэкап tsa.db.bak-before-reopen-bldg14-*).

Связано: [[project_tsa_timeline]], [[project_ontime_heartbeat]] (триггеры закрытия), [[feedback_no_confirms_ontime]].
