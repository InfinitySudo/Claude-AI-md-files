---
name: React select fallback on missing option
description: <select value=X> где X не значится в <option> молча показывает первый option — UI начинает врать про данные
type: feedback
originSessionId: 76d69d60-e032-4a5a-9b40-2a8d16aee677
---
`<select value={x}>` в React: если `x` не совпадает ни с одним `<option value=…>`, браузер тихо выбирает первый option без выделения. Никакого предупреждения. UI рендерит роль/статус/что-угодно ≠ данным в БД.

**Why:** 2026-05-03 Артём прислал screenshot где ARTEM TKACHENKO в Roster показан как "Foreman", хотя в БД у него `roster.role='director'` и `users.role='director'`. RosterPage держал `ROLES = ['foreman', 'installer', 'helper', 'service', 'delivery']` — без management ролей. Dropdown получал `value='director'` без подходящего option и рисовал первый = "Foreman". Артём верил UI, потратили время на поиск несуществующего foreman-assignment в БД.

**How to apply:**
- Когда Артём говорит «уберите X из роли Y» — сначала проверить `users.role`, `roster.role`, `projects.foreman_id`, `project_foreman_history`, `foreman_team`, `project_helpers`, `project_installers` для этого user_id. Если везде роль уже правильная — это UI bug, не data bug.
- При добавлении новой роли в backend (ROLES/POSITIONS) — grep frontend на хардкод-списки: `'foreman'.*'installer'` и т.п. Не один RosterPage с этим: ProjectsPage / TeamPage / Rankings могут иметь свои короткие списки.
- Источник истины ролей в проекте — backend `POSITIONS` (`main.py:149`). Frontend не должен дублировать конкурирующие подмножества; держать `ALL_ROSTER_ROLES` синхронизированным.

**Связанный баг (i18n.js дубликат-ключи, 2026-05-03):** В `src/lib/i18n.js` ключи `installer`/`helper` фигурировали ДВАЖДЫ в каждой языковой секции — Title Case сверху + lowercase ниже. JS object literal: последний дубликат побеждает → badge показывал маленькую букву. `mechanic` отсутствовал вовсе → `t('mechanic')` отдавал ключ '`mechanic`' (lowercase). При добавлении новой роли в `POSITIONS` — добавить её в EN/RU/UA секции i18n.js с Title Case и проверить grep'ом что ключ не задублирован lowercase-версией для inline-текста.
