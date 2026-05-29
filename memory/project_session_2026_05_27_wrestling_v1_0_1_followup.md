---
name: session-2026-05-27-wrestling-v1-0-1-followup
description: "Wrestling v1.0.1 follow-up (commit 0621ad4) — owner push на application, Discover region/city chips, Sparring tab state-save через sessionStorage; плюс recovery от `NameError: List` краша backend"
metadata: 
  node_type: memory
  type: project
  originSessionId: b95ea449-cc93-4524-8750-cf6726e7eba6
---

## Wrestling v1.0.1 follow-up (commit 0621ad4, 2026-05-27)

### Что было сломано
- Артём прислал видео «Something went wrong» при создании спарринга.
- В `journalctl -u wrestling-api` нашёлся `NameError: name 'List' is not defined` в `class TournamentCreate(BaseModel)` (line 408) и `TournamentUpdate` (line 432) — где-то использовался `List[…]` без `from typing import List`. systemd рестартил каждые 4 секунды (логи 23:57:59→23:58:27 MDT), фронт ловил 500/connection-refused → toast «Something went wrong».
- К моменту дебага код уже был исправлен на `Optional[list]`, сервис стабильно поднялся в 23:58:34. Прямой `POST /api/tournaments` с минтованным coach JWT (`sub` — это `users.id` int, не email!) вернул 200 OK.

### Что добавлено в этом коммите (3 follow-up из v1.0.1 todo)
1. **Push owner на cross-club application** — в `create_application` после INSERT:
   ```python
   owner = query_one(conn, 'SELECT id FROM users WHERE LOWER(email) = LOWER(%s)', (t.get('coach_email') or '',))
   if owner:
       _wp_notify(conn, owner['id'], kind='sparring_application',
                  title=f"New application to «{t['name']}»",
                  body=f"{applicant_label} requested (N athletes)",
                  link_url='/sparrings')
   ```
   `coach_email` — это owner; нет `creator_user_id` колонки → JOIN через email.

2. **Discover region/city chips** — `DiscoverPublicSparrings`:
   - `scope` ∈ `country|region|city`, default `country`, персист в `sessionStorage('sparring:discoverScope')`.
   - 3 chip-кнопки, disabled если у тренера `user.region`/`user.city` пустое.
   - Filter `otherClubs` case-insensitive по `t.region`/`t.city` vs `user.region`/`user.city`.
   - Empty-state подсказывает «Switch to 🌐 Country to widen the search».

3. **Sparring tab state-save** — `selected` (id открытого спарринга) в `TournamentsPage`:
   - Init из `sessionStorage('sparring:selected')`, write в useEffect, remove при null.
   - Зачем: tap match → `navigate('/scoreboard/{mid}')` → ← back → React пересоздаёт `TournamentsPage`, без persistence `selected` сбрасывался в null и юзер падал на пустой список.

### Грабли (избегать в будущем)
- **JWT `sub` = int users.id, НЕ email.** В тесте сначала намитил с `sub:email` → 500 `ValueError: invalid literal for int()`. Смотри `get_current_user` в main.py:97.
- **`_wp_notify` сигнатура**: `notify(conn, user_id, kind, title, body=None, link_url=None)` (web_push.py:97). Two-track: insert в `notifications` + best-effort web-push, не падает если у юзера нет subscriptions.
- **Build/restart**: `npm run build` пересобирает `dist/`, `systemctl restart wrestling-api` бэкенд. Cwd должна быть в `/root/Wrestling-Performance-Tracker`.

**Why:** Артём попросил доделать v1.0.1 follow-up: «Push-уведомление owner-у когда приходит application. Filter Только мой регион/город в Discover. Sparring state-save при выходе из scoreboard».
**How to apply:** При следующих изменениях Discover/TournamentDetail помнить про sessionStorage ключи `sparring:discoverScope` и `sparring:selected`. При добавлении новых event-ов в спаррингах — звать `_wp_notify` тем же паттерном.

Связано: [[project-wrestling-v2]], [[project-session-2026-05-26-wrestler-card-competitions]].
