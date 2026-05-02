---
name: JSON-конфиг trading_v3_artem.json содержит плейсхолдеры ${VAR}
description: trading_v3_artem.json хранит секреты как ${DB_PASSWORD}/${BYBIT_API_KEY}; код должен разворачивать их через env_config.expand_env_vars
type: feedback
originSessionId: 58ce88b1-9a66-41b4-a3bc-efe3e6843864
---
`config/trading_v3_artem.json` (файл отслеживается в git) держит секреты как строковые плейсхолдеры: `"password": "${DB_PASSWORD}"`, `"api_key": "${BYBIT_API_KEY}"` и т.п. Это сделано, чтобы настоящие значения не попадали в git-историю.

Любой код, читающий этот JSON, ДОЛЖЕН после `json.load()` пропустить его через `env_config.expand_env_vars(cfg)`. Иначе Postgres/ByBit получают буквальную строку `${DB_PASSWORD}` и падают с auth failed.

**Why:** 2026-04-10 TradingBot (main_bot_v3.py) падал на старте с `password authentication failed for user "trading_bot"`, потому что `DatabaseConnector` получал `config['database']['password'] == "${DB_PASSWORD}"`. `signal_bot_v3_websocket.py` и `strategy_switcher_v3.py` не упали только потому, что берут пароль напрямую из `env_config.DB_PASSWORD`, минуя JSON.

**How to apply:**
- Если добавляешь новый код, читающий `trading_v3_artem.json`, оборачивай: `cfg = env_config.expand_env_vars(json.load(f))`
- Не пихай реальные секреты обратно в JSON — файл в git
- `expand_env_vars` рекурсивно обходит dict/list/str и подставляет из `os.environ`, неизвестные переменные оставляет как есть
