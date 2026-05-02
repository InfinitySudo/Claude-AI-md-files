---
name: Dashboard-First Workflow
description: Артём хочет чтобы ВСЕ изменения настроек и операции делались через dashboard UI/endpoint, не напрямую в файлах/SQL/CLI
type: feedback
originSessionId: a080f8b3-13b0-4be7-8650-c581d878ad77
---
**Правило**: любое изменение конфигурации или операцию с UI-представлением — делать **через dashboard endpoint**, не напрямую (редактирование JSON, SQL UPDATE bot_settings, CLI `python scripts/...`).

**Why:**
1. Каждое изменение через dashboard = working test цепочки UI → API → storage → live bot read. Если путь сломан (dead routing, mismatched path) — проявится сразу.
2. Много раз находили баги вида "dashboard пишет в X, бот читает из Y, настройки не применяются" (tp*_percent, max_positions, be_* routing). Если бы Артём правил через UI, баги вскрылись бы в момент задания значения.
3. `ga_status.json`, `settings cache`, `rollback snapshots` — всё это dashboard поддерживает сам. CLI обходит — UI висит со старым стейтом.
4. Последний writer по timestamp решает что активно (last-write-wins для tp/ga) — прямое редактирование JSON без timestamp ломает логику.

**How to apply:**
- **Настройки**: `POST /api/settings/<key>` с `{"value": N}`. Не SQL UPDATE, не правка trading_v3_artem.json.
- **GA run**: `POST /api/ga/run` с `{"symbols":[...],"pop":40,"gens":30,"workers":3}`.
- **GA apply rank**: `POST /api/ga/apply` с `{"confirm_phrase":"APPLY GA","rank":1}`.
- **Service restart**: `POST /api/services/<name>/<action>` (start/stop/restart).
- Если endpoint не поддерживает параметр — **сначала добавить** в endpoint + SETTINGS_REGISTRY, потом использовать.

**Исключения** (только когда UI действительно нет):
- Фоновые скрипты без UI: `fetch_bybit_archive.py`, миграции схемы БД
- Debug/one-off эксперименты — но ПОСЛЕ них вернуть в dashboard управление
- Экстренные ситуации где dashboard недоступен (тогда фиксить dashboard приоритетно)

**При аудите**: проверять что dashboard writes to X == bot reads from X (grep `setting_name` vs `config.get(path)`). Любой mismatch = dead setting, фиксить немедленно.
