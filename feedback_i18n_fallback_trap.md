---
name: i18n-fallback-trap
description: "react-i18next `t('key') || 'Default'` НЕ работает — t() возвращает сам ключ как truthy при отсутствии перевода, fallback никогда не срабатывает. UI показывает буквально 'login.country'."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: be849f60-63be-4c16-b36d-b222e4c0a460
---

**Правило:** в react-i18next-проектах (`Wrestling-Performance-Tracker`, любой будущий) **никогда** не писать `t('key') || 'Default'` или `t('key') ?? 'Default'`. Использовать встроенный механизм:

```js
t('login.country', 'Country *')                     // positional default
t('login.country', { defaultValue: 'Country *' })   // explicit
```

ИЛИ просто добавить ключ во все нужные locale JSON-файлы (минимум `en.json`, остальные через `fallbackLng:'en'`).

**Why:** при отсутствующем ключе `i18next` по умолчанию возвращает строку самого ключа (`'login.country'`), которая truthy. Поэтому `||` fallback не срабатывает, и UI показывает буквально `login.country` вместо «Country *». Поймано визуально 2026-05-26 через Playwright verify Wrestling-app — на скриншоте `01_register.png` были `login.country`, `login.region`, `login.app_policy_title` и т.д. в плейсхолдерах и заголовках. Без verify-прогона улетело бы в прод.

**How to apply:** перед коммитом нового UI с `t()` — либо положительно добавить ключ в `src/i18n/en.json` (фолбэк-язык), либо использовать второй аргумент `t()` для дефолта. Линт-правило / grep пред-коммита: `git grep -nE "t\([^)]+\)\s*\|\|" src/` должен возвращать 0 строк (кроме хорошо обоснованных кейсов).

Связано: [[session-2026-05-26-wrestling-app-policy]], [[project-wrestling-i18n-10langs]].
