---
name: project_tsa_self_switch_project
description: OnTime — installer/helper сам переводит себя между объектами; при работе сегодня обязан сначала сдать отчёт; форман не дёргается
metadata: 
  node_type: memory
  type: project
  originSessionId: 5b904a97-9e9f-4dd3-8802-6c3fef431230
---

OnTime: работник (installer/helper) сам выбирает объект на сегодня и переходит между объектами **без формана**. Кнопка «Сменить объект» на `InstallerHomePage` → `SwitchProjectModal.jsx` со списком всех active-объектов компании (поиск).

**Логика (backend `backend/main.py`):**
- `GET /api/me/switchable-projects` — все active cladding/masonry объекты компании (status!='done', не archived, не service/delivery); флаг `is_current`, `has_open_session`. Без денег.
- `POST /api/me/switch-project {to_project_id}` (self-only, `_is_management` → 403):
  - уже на target → `already_here`.
  - нет текущего объекта → self-pin к target (`requires_report:false`).
  - есть часы/открытая смена сегодня на текущем A → **закрывает смену** (`_close_open_sessions_on_transfer`, end_reason='transfer'), создаёт `pending_transfers` (requested_by=self, auto_pulled=0), `requires_report:true` + `from_project_id`. Фронт ведёт на форму отчёта; сабмит (`kind='transfer'`) завершает перевод через `_apply_pending_transfer` в `create_report`. Работник остаётся в crew A **до сдачи отчёта**.
  - нет часов сегодня → `_apply_pending_transfer` сразу.
  - оба формана получают post-factum уведомление (`_notify_self_switch_foremen`) — информируем, не спрашиваем.

**Принципы (Артём):** геолокацию НЕ используем как гейт (ненадёжна в зданиях); привязка = QR-чек-ин + явный выбор; часы автозаполняются из QR-сессии → не уедут на чужой объект; отчёт обязателен перед уходом → ничего не теряется.

Переиспользует transfer-флоу: см. [[project_tsa_transfer_flow]]. Связано: [[project_ontime_heartbeat]], [[feedback_ontime_report_crew_guard]].
