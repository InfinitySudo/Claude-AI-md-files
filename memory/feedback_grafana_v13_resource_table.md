---
name: feedback-grafana-v13-resource-table
description: "Grafana 13 хранит дашборды в новой `resource` таблице, не в `dashboard`; SQLite-фикс возможен с restart'ом сервера"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

Grafana 13+ переехала на «App Platform»: dashboards/folders/datasources хранятся в **`resource`** таблице (`/var/lib/grafana/grafana.db`), а не в legacy `dashboard`/`folder`/`data_source`. У старых таблиц `COUNT(*)=0` при работающем UI — легко перепутать с «нет дашбордов».

**Why:** 2026-05-13 — `SELECT COUNT(*) FROM dashboard` вернул 0, при том что Артём смотрел `4BotsBybit — Live`. Реальные данные в `resource WHERE resource='dashboards'`, поле `value` — JSON в формате `{kind, apiVersion: dashboard.grafana.app/v0alpha1, metadata, spec, status}`.

**How to apply (read):**
```sql
SELECT value FROM resource
WHERE name='<dashboard-uid>' AND resource='dashboards';
```
JSON: `value.spec.panels[].targets[].rawSql` — SQL queries; `value.spec.templating.list` — variables.

**How to apply (write):** UI/API всегда предпочтительнее. Для blind DB-фикса (если нет admin-пароля):
1. `systemctl stop grafana-server` (чтобы не словить in-memory cache)
2. Backup `cp grafana.db grafana.db.bak.<date>`
3. Python: load JSON → mutate `rawSql` (или что нужно) → `json.dumps(separators=(',',':'))`
4. `UPDATE resource SET value=?, resource_version=? WHERE …` — поднимать `resource_version` до nanos-since-epoch (`int(time.time()*1e9)`).
5. Также синкнуть `UPDATE resource_version SET resource_version=?` для (`group=dashboard.grafana.app`, `resource=dashboards`).
6. По возможности `INSERT INTO resource_history` для аудита (если таблица есть).
7. `systemctl start grafana-server`; bleve переиндексирует автоматически (`logger=bleve-backend ... reason=search`).

**Гремлины:**
- `dashboard` таблица legacy — не путать с актуальной `resource`.
- Stat-panel-ы требуют timestamp-колонку (`SELECT updated_at AS time, …`); без неё рендерят "No data".
- `$__timeFilter()` обёрнут вокруг колонки в WHERE — выбирать поле, которое реально двигается во времени (`exit_time` для PnL-серий, `updated_at` для лайфтайм-стат).
- API key схема: `api_key.is_revoked`, `api_key.role` (NOT NULL); генерация токена руками сложна — проще restart-через-DB.

Связано с [[project-unversioned-prod-state]] (Grafana не в git), [[project-grafana-alerts]] (Trading Alerts → TG).
