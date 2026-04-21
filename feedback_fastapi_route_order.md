---
name: FastAPI sibling-path collision
description: При добавлении endpoints в main.py избегай коллизий с уже существующими {param} путями
type: feedback
originSessionId: 4513b864-6df3-4629-8b5d-c3e0f8273f0f
---
В OnTime backend (`/root/ontime/backend/main.py`) есть `GET /api/reports/{rid}`. Любой новый
двухсегментный endpoint типа `/api/reports/<word>` будет матчиться как `{rid}` и падать с
int_parsing validation error (попытался `eligible-extras` → 422).

**Why:** FastAPI проверяет routes в порядке декларации. `{rid}` объявлен раньше, и FastAPI
не пробует следующий маршрут, если текущий подошёл по форме.

**How to apply:** новые sub-resources под коллекцией с `{id}`-параметром делай трёхсегментными
(`/api/reports/extras/eligible`, `/api/reports/prefill/hours`) вместо плоских
(`/api/reports/eligible-extras`). Или декларируй специфичный путь выше `{id}`-маршрута.
