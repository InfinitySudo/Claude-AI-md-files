---
name: Dashboard settings apply chain (self-sufficient, no ControlBot needed)
description: POST /api/settings/<key> teper polnostyu primenyaet nastroiki — obnovlyaet vse tablicy + rebootayet servis. Artem planiruet otkazatsya ot TG ControlBot.
type: project
originSessionId: a50e8fb7-4ba7-4e12-826b-ccf591fe559e
---
**До 2026-04-22:** dashboard сохранял настройки, но:
1. `forced_strategy` писался только в `bot_settings` — а TradingBot читает из таблицы `current_strategy`. ControlBot обновлял обе; dashboard — нет.
2. Ни frontend, ни бэк не дёргали `systemctl restart` — показывалось "✓ saved — restart X to apply", и всё зависало.

**После 2026-04-22:**
- `_apply_forced_strategy_side_effects()` в `dashboard_api_v3.py` — зеркалит `ControlBot._set_strategy_mode`: `bot_settings` + `current_strategy` + `strategy_switch_log` атомарно, `reason='Manual switch (dashboard)'`.
- `POST /api/settings/<key>` — если `restart: <service>` в SETTINGS_REGISTRY, бэк сам вызывает `systemctl restart <service>`. Дашборд не рестартит сам себя (`dashboard-api` пропускается). Для batch-edit: `{"value": X, "auto_restart": false}`.

**Why:** Артём собирается отказаться от TG ControlBot, всё управление должно быть через dashboard. Любой клиент (UI / curl / mobile app) — моментально применяет.

**How to apply:**
- Никогда не править конфиги руками (`trading_v3_artem.json`, `signal_bot_config.json`, `bot_settings`) — только через `POST /api/settings/<key>`. Атомарность + валидация + авто-рестарт + аудит.
- Если нужна новая настройка — добавить её в `SETTINGS_REGISTRY` (dashboard_api_v3.py:~600-695) с полями `backend`/`path`/`restart`/`kind`/`enum`. Side-effects (как для `forced_strategy`) — только если апдейт одной таблицы недостаточен.
- Canonicalization systemd имён в POST: `signal_bot` → `bybit-signalbot` через `svc_map`. Если добавишь новый short-name в registry — расширь карту.

**Gotcha:** `bybit-strategy-switcher` тихо теряет DB-pool (`connection already closed`) — в AUTO режиме молча простаивает. Проверять `journalctl -u bybit-strategy-switcher --since "2 hours ago" | grep -i "connection"`. Если есть — `systemctl restart bybit-strategy-switcher`. Root-cause не фикшен, пока только monitoring.
