---
name: Legacy DB не коммитить
description: Production-данные TSA из legacy БД нельзя в публичный репо OnTime
type: feedback
originSessionId: 7307290c-93f4-4995-a318-269609a49e02
---
**Rule:** файлы `migration/*.db` не должны попадать в git ни при каких обстоятельствах.

**Why:** `migration/legacy.db` (2.2 MB) — копия production БД клиента TSA с 7909 реальных отчётов, 69 работниками с tg_id, зарплатами, phone-номерами. Репо `github.com/InfinitySudo/OnTime` публичный — утечка приватных данных клиента.

**How to apply:**
- `migration/*.db` добавлено в `.gitignore`. Не убирать.
- При создании новых dump-файлов (`*.sqlite3`, `*.sql`) — проверять `git status` перед `git add -A`.
- Если случайно застейджено — `git restore --staged <file>` до коммита, а если уже в истории — срочно `git filter-repo` / повторный push с rewritten history + ротация любых засвеченных credentials.
