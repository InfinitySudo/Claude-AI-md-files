---
name: SQLite ISO timestamp comparison trap
description: SQLite datetime('now') пишет с пробелом, Python datetime.isoformat() пишет с T — лексикографическое сравнение режет записи в день cutoff'а
type: feedback
originSessionId: fbcba95d-de8d-4157-b95c-f02a54a7cfac
---
SQLite функция `datetime('now')` записывает timestamp в формате `"2026-04-20 18:28:38"` (пробел между датой и временем). Python `datetime.isoformat()` по умолчанию даёт `"2026-04-20T04:08:13"` (с `T`). При сравнении строк в SQL `WHERE awarded_at >= ?` — сравнение **лексикографическое**: символ ' ' (0x20) < 'T' (0x54), поэтому записи в день cutoff'а **отфильтровываются** как "слишком ранние", даже если по времени они позже cutoff'а.

**Симптом:** "куда пропали 2 поинта?" — пользователь видит 38 вместо 40, потому что 2 записи на дату ровно 7 дней назад выпали из `period='week'` фильтра.

**Why:** Найдено 2026-04-26 в OnTime: Igor Kurinnyy показывал 38 поинтов вместо 40. Корневая причина — `_period_cutoff().isoformat()` против `awarded_at` в `punctuality_points` и `closed_at` в `project_scores`. Те же 5 мест в `main.py` (rankings, badges, payroll endpoints) использовали `.isoformat()`.

**Fix:** `cutoff.isoformat(' ')` — передать `sep=' '` в isoformat, формат становится идентичен SQLite `datetime('now')`.

**How to apply:** Любой Python код, сравнивающий строковые timestamp'ы из SQLite, должен использовать тот же разделитель что и БД. Альтернативы: `.replace('T', ' ')`, либо `datetime(col) >= datetime(?)` в SQL (SQLite парсит оба формата). Если видишь несовпадение между `COUNT(*)` в БД и UI-числом — первое подозрение это timestamp boundary в WHERE.
