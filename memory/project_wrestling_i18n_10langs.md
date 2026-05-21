---
name: project-wrestling-i18n-10langs
description: Wrestling tracker поддерживает 10 языков (en/ru/uk/pl/ar/fa/zh/ja/pa/es) с RTL и header-dropdown для смены без выхода
metadata: 
  node_type: memory
  type: project
  originSessionId: c9d2b899-f272-4e25-b502-fa1e0f5284ca
---

С 2026-05-19 (commit b3a576e) wrestling-tracker мультиязычен на 10 локалях:

- Файлы: `src/i18n/{en,ru,uk,pl,ar,fa,zh,ja,pa,es}.json` (10 локалей)
- Регистр и `setLang()` живут в `src/i18n/index.js`. `setLang(code)` ставит `localStorage.wpt_lang`, переключает `i18next` и применяет `document.documentElement.dir = rtl|ltr` (rtl для `ar` и `fa`).
- В `<header>` есть `<LanguageSwitcher variant="dropdown" />` — глобус + флаг + popover, рядом с колокольчиком. Без variant даёт legacy chip-row для ProfilePage.
- Старые ключи: `login.*`, `nav.*`, `common.*`, `policy.*`, `members.*`, `norms.*`, `spars.*`, `rankings.*`.
- Новые секции 2026-05-19: `pages.*` (заголовки страниц), `actions.*`, `stats.*` (Athletes/Sessions/Pending/Reviews/Total Points/Norms Done/Trainings), `dashboard.*` (Coach panel CTAs), `sparring_section.*`, `leagues_section.*`, `camps_section.*`, `push_notif.*`.

**Why:** Артём хочет привлекать клубы в Канаде с разной диаспорой (украинцы, поляки, иранцы, китайцы, японцы, индийцы-пенджабцы, арабы).

**How to apply:**
- Любую новую UI-строку оборачивай в `t('section.key')` и **добавляй ключ во все 10 файлов**, иначе fallback на en для остальных.
- Если страница использует подкомпонент (например `TournamentDetail`, `ProfileTab`, `CreateLeagueForm`, `LeaguesList`, `CardContent`, `PushNotificationsCard` и т.п.) — в нём свой `const { t } = useTranslation();`. Это уже ловилось дважды (b3a576e и fef9e1b) — `replace_all` `>Total Points` подменил строку и внутри `ShareableCard/CardContent`, который не имел хука. Грепай `\{t\(` против `useTranslation()` по каждому `function ` в файле перед билдом.
- Для RTL не используй `ml-*`/`mr-*` без проверки — Tailwind не зеркалит сам. Лучше `ms-*`/`me-*` (logical) или `gap-*`.

Связано: [[project_wrestling_v2]], [[feedback_nginx_uploads_regex_trap]].
