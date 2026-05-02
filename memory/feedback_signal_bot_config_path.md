---
name: signal_bot_config.json — two files, one orphan
description: Canonical signal config path is env_config.SIGNAL_BOT_CONFIG_PATH (src/signal_bot_config.json). The root-level copy is orphaned — writes there do nothing.
type: feedback
originSessionId: 02a721df-beff-4bfd-bf57-391bd21672c8
---
There are TWO `signal_bot_config.json` files in the repo and one of them is dead. Do NOT write to the root-level one.

- **Canonical (reader + writer): `src/signal_bot_config.json`** — referenced via `env_config.SIGNAL_BOT_CONFIG_PATH`. `control_bot_simple_v3._load_signal_config/_save_signal_config` use this. `signal_bot_v3_websocket.py:65` hardcodes the absolute path to this same file. **This is the one the bot actually reads** at signal-check time.
- **Orphan: `/root/4BotsBybit-Trading/signal_bot_config.json`** (top-level). Still tracked in git for historical reasons but nothing reads it. Writes here are silently lost.

**Why this matters:** I wasted time in 2026-04-11 by hardcoding `SIGNAL_JSON_PATH = '/root/4BotsBybit-Trading/signal_bot_config.json'` in `dashboard_api_v3.py` (the new Settings tab writer), then testing the endpoint via curl, then seeing "success" responses while the bot kept using the old values. The fix was `SIGNAL_JSON_PATH = env_config.SIGNAL_BOT_CONFIG_PATH`. The orphan file was then reverted via `git checkout`.

**How to apply:**
- Any code that touches signal criteria must go through `env_config.SIGNAL_BOT_CONFIG_PATH`. Never hardcode the path and never "simplify" to the top-level file.
- If you notice the root-level `signal_bot_config.json` is out of sync with the `src/` one, the `src/` one is truth. Revert the root copy.
- Cleanup debt: the orphan file could be deleted from the repo outright, but it's tracked and any removal needs a proper `git rm` commit. Low priority.
