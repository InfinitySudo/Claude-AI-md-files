---
name: OnTime daily-report crew guard
description: /api/reports rejects 403 if user is not on the project crew; bypass paths and how to debug "you are not on this project crew" errors
type: feedback
originSessionId: b4e56692-a9c8-43a7-8ec4-f5c05ab54499
---
С 2026-04-28 endpoint `POST /api/reports` (`backend/main.py` ~line 4193) блокирует отчёт от пользователя, который не значится в крю проекта. Это решает проблему «осиротевших» отчётов от installer'ов, которых не добавили в `project_installers/helpers`.

**Why:** до 2026-04-28 endpoint принимал отчёт от любого user × project (любой company member). Это создавало orphan'ов: они есть в `daily_reports`, но не в `project_installers/helpers`, и их не видно во вкладке Team. Кейс: Pavlo Kosts, Taras Ivanets подавали отчёты на Bldg 700, но не значились на нём.

**How to apply:**
- Allow path (любое из):
  1. `_is_management(user)` — admin/pm/vp/director постят за кого угодно
  2. `pending_transfers.from_project_id == project_id` — закрывающий отчёт при переводе
  3. `projects.foreman_id == user.id`
  4. `project_installers` row exists
  5. `project_helpers.removed_at IS NULL` row exists
- Иначе → `HTTP 403 "You are not on this project crew — ask the foreman to add you."`

**Когда отчёт ломается у работника:**
1. Check `project_installers WHERE installer_id=X` — пусто? добавить через UI Team или INSERT
2. Check `project_helpers WHERE user_id=X AND removed_at IS NULL`
3. Если был `pending_transfer` от другого проекта — должен сначала закрыть FROM-проект
4. Bulk-recovery script: см. `INSERT OR IGNORE INTO project_installers SELECT DISTINCT ... FROM daily_reports ...` (использовался 2026-04-28 для backfill 19 пар)
