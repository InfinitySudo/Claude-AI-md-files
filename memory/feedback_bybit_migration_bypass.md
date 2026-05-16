---
name: feedback-bybit-migration-bypass
description: "CLAUDE.md правила 4BotsBybit-Trading (нет правки .env, нет stop systemd, нет закрытия real-поз) — bypass-имо ТОЛЬКО при явном разрешении Артёма на конкретную миграционную задачу."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4549af2c-3ca5-42b1-8cf2-f9e95b8aeb3c
---

CLAUDE.md в `/root/4BotsBybit-Trading` запрещает:
1. Прямую правку `.env` / `config/trading_v3_artem.json` (только через Dashboard API)
2. `systemctl stop bybit-*` (только restart)
3. Закрывать реальные позиции на Bybit

**Why:** Production trading — ошибки стоят денег. Правила написаны как guard от случайных действий.

**How to apply:**
- В обычной работе — следовать правилам строго.
- Bypass допустим **только при явном разрешении Артёма** в текущей сессии на конкретную миграционную операцию. Примеры явного разрешения: «Force-close все 20 поз», передача API ключей с подразумеваемой ротацией, прямое «делай stop сервиса X».
- Перед нарушением — сообщить вслух какое правило CLAUDE.md нарушаешь и почему (5 сек grace на отмену).
- Dashboard API намеренно НЕ имеет endpoint'а для смены `BYBIT_*` ключей (security). Поэтому при ротации ключей прямая правка .env неизбежна.
- Force-close нужно делать с **блокировкой signal-source** до операции (иначе TradingBot откроет новые позы пока ты чистишь старые — был race на 3 позиции при миграции 2026-05-15). Способы блока: 1) `restart` бота с пустым ключом (он не сможет торговать с $0 capital); 2) поставить strategy_mode=PAUSED через [[project-trading-state-softgate]] (только фриз стратегии на CONS); 3) cancel-all orders первым шагом (но не блокирует новые position-open).
- Связано: [[bybit-3-sub-architecture]], [[feedback-bybit-env-symlink]].
