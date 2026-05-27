---
name: feedback-pwa-stale-bundle
description: Wrestling PWA сбрасывает кэш через CACHE bump в sw.js. НЕ делать auto-reload по controllerchange/sw-activated (loop). Self-heal через React Query onError с TTL gate.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c9d2b899-f272-4e25-b502-fa1e0f5284ca
---

Несколько раз попадались в loop'ы при попытке решить "stale bundle" в wrestling PWA. Уроки:

## Что НЕ делать

1. **`controllerchange` + `window.location.reload()`** — на v8→v9 swap controller уже claimed, событие фигачит каждый refresh → infinite loop.
2. **SW `postMessage({type:'sw-activated'})` после `clients.claim()` + reload на receive** — то же самое, broadcasts при каждой активации.
3. **`window.__apiReady` setTimeout 6s + reload если flag missing** — на code-split bundles api chunk не успевает выполниться за 6s → loop.
4. **`sessionStorage.cwResetDone` sticky gate** — если сработал раз, второй stale-bundle уже не починить.

## Что РАБОТАЕТ

- **`CACHE = 'wrestling-vN'`** bump + `activate` deletes ВСЕ keys + `clients.claim()`. Этого хватает на normal navigation.
- **SW bypass cache для navigation / index.html / sw.js**: иначе stale `index.html` указывает на старый JS chunk forever.
- **Daily cachebuster** `/sw.js?d=YYYY-MM-DD` для devices что cache'ят sw.js на час.
- **`reg.update()`** poll каждые 30 мин для long-lived PWA sessions.
- **React Query `QueryCache.onError + MutationCache.onError`** в App.jsx → `tryHardResetOnce(err)`: если message содержит "is not a function", `unregister()` всех SW + `caches.delete()` всех + `window.location.reload('/?_=' + ts)`. Gate через `localStorage.cwResetTs` с **10-минутным cooldown** (не sessionStorage sticky).
- **Surface error**: в queries показывать `query.error.message` красным вместо тихого "Nobody matches these filters" — пользователь сразу видит проблему.

## Bonus baggage gotchas

- **Дублирующиеся `admin:` ключи** в литерале `export const api = {...}` — JS silently keeps только последний (cross-club методы исчезают). Если нужны несколько групп — отделить в `apiExtra` объект и `Object.assign(api.section, api.sectionExtra)` после export.
- **Code-split chunks**: api/client.js должен быть **статически** импортирован в каждом компоненте который его использует. Динамический `import('@/api/client').then(...)` ломает chunk shape.

## Связано
- [[project_wrestling_v2]]
- [[project_wrestling_super_admin]]
