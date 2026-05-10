---
name: TG ControlBot slash commands добавлены 2026-05-08
description: @ControlByBitTradingBot теперь принимает /status /balance /pause /resume /help; auth через owner_id; добавлены в src/control_bot_simple_v3.py
type: feedback
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
Rule: Управление trading-state и быстрый status доступны ТОЛЬКО в TG бота `@ControlByBitTradingBot` (`bybit-control-bot.service`, env `TELEGRAM_CONTROL_BOT_TOKEN`). НЕ в `@TradingStatistic8Bot` (это outbound-only reports) и НЕ в других бот-аккаунтах.

**Why:** На сессии 2026-05-08 добавлены slash commands к существующему inbound polling loop в `src/control_bot_simple_v3.py` (там уже был `/start` + callback handlers). Цель — управлять ботом с телефона без захода в dashboard.

**Команды (все proxy к существующим `/api/*`):**
- `/status` → wallet, state, verdict, open count, RO active flag
- `/balance` → wallet/equity/uPnL + last 5 closed real_trades
- `/pause` → POST `/api/trading-state/pause` reason="manual via tg"
- `/resume` → POST `/api/trading-state/resume`
- `/help` → список команд

**Auth:** `chat_id == self.owner_id` (env `TELEGRAM_CHAT_ID`). От любого другого chat_id команды игнорируются с warning в журнал. owner_id хардкоден `504609639` в `control_bot_simple_v3:42` (parameterizable если понадобится).

**How to apply:**
- Если Артём пишет «бот не отвечает на /status» — `journalctl -u bybit-control-bot --since '5min ago'` ищем «slash command from non-owner» (auth fail) или Tracebacks
- Если хочется новых команд: добавить в dispatcher map в `_handle_slash_command` + write helper `_cmd_<name>(self, chat_id)`
- НЕ перепутать с TG digest бот'ом (`@TradingStatistic8Bot`) — он outbound only через `claude_notifier.send_telegram`
