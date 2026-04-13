---
name: ControlBot при shutdown убивает все торговые боты
description: Kill старого ControlBot или остановка его через systemd triggers shutdown-хендлер, который шлёт SIGTERM SignalBot+TradingBot+StrategySwitcher
type: feedback
originSessionId: 58ce88b1-9a66-41b4-a3bc-efe3e6843864
---
У `control_bot_simple_v3.py` есть shutdown-хендлер, который при завершении процесса посылает SIGTERM всем управляемым им торговым ботам (`telegram_bot_runner_v3.py`, `main_bot_v3.py`, `strategy_switcher_v3.py`). То есть «убить ControlBot» = остановить ВСЮ торговлю.

**Why:** 2026-04-10 во время миграции ControlBot я сделала `kill <old_pid>` — через секунду TradingBot получил SIGTERM и выключился; Signal/Switcher тоже. Я не заметила, потому что проверяла только `pgrep control_bot_simple_v3`. Торговля стояла ~36 минут, пока проблема не была найдена по логам.

**How to apply:**
- Если нужно перезапустить/обновить ControlBot, будь готов сразу же поднять торговые боты (нажать 🟢 Start в Telegram или запустить руками).
- После любого `kill` или `systemctl restart bybit-control-bot.service` ВСЕГДА проверяй весь пул: `pgrep -af "telegram_bot_runner_v3|main_bot_v3|strategy_switcher_v3"` — не только control-бота.
- Лучше предупредить пользователя перед операцией, что торговля временно остановится.
