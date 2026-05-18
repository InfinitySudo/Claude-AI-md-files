---
name: wet-frontend-backend-drift
description: "wife-english-tutor: frontend часто написан с endpoints которых нет на backend; sweep всегда перед \"проверкой работы\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f70afc19-ea49-486a-8c9e-b332332d417d
---

В wife-english-tutor была накопленная драфт-инфраструктура: frontend (read.html, app.js) и backend модули (bot/reading.py, bot/vocab.py, bot/pronounce.py) разрабатывались параллельно, но **endpoints в web/app.py не регистрировались**. Liliya видела 404 на нескольких вкладках.

**Why:** видимо часть прошлых сессий заканчивалась без коммита integration-слоя (или коммитили только bot/ + static/, забывая web/app.py).

**How to apply:** при любом «X не работает» в wet — делай sweep:

```bash
echo "=== FRONT ==="; grep -oE '"/api/[^"]+"' web/static/*.html web/static/*.js | grep -oE '/api/[^"]+' | sort -u
echo "=== BACK ===";  grep -oE '@app\.(get|post)\("/api/[^"]+"' web/app.py | grep -oE '/api/[^"]+' | sort -u
```

Дельта = твой fix-list. son-french-tutor — reference implementation (всегда впереди по фичам, копируй handlers оттуда).

Помни:
- `/api/books` должен возвращать `progress: {book_id: last_chapter}` — иначе read.html bookCard крашится на `state.progress[b.id]` (баг id=13 Speckled Band у Liliya 2026-05-16)
- `_auth()` возвращает `(tg_id, name)`; для user-specific endpoints — `db.upsert_user(tg_id, name=name)` → user_id
- Auth header: `X-Telegram-Init-Data`; `WET_DEV_TG_ID` env даёт dev-bypass
- Defensive frontend: `data.field || {}` чтобы не падать когда бэк забыл поле
