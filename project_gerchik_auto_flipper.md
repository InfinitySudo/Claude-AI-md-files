---
name: gerchik-auto-flipper
description: "Модуль auto_flipper.py — переворачивает зарегистрированные counter-trend позиции при возврате к BE+комиссии; state, как добавлять кандидаты"
metadata: 
  node_type: memory
  type: project
  originSessionId: fdfe8ecb-6a09-4f66-8869-b95289919a5d
---

`/root/gerchik-trading-agent/src/auto_flipper.py` — вызывается из main loop каждые 60s, проверяет зарегистрированные позиции и делает Long↔Short flip когда цена возвращается к break-even + small buffer.

**Why:** Артём 2026-05-19 хочет «дать» counter-trend Long выйти в небольшой плюс (покрыть комиссии) и переворачиваться в trend-aligned Short, а не сидеть в убыточной позе до SL.

**How to apply:**
- Кандидаты в `CANDIDATES` dict (hardcoded). Добавить нового — `{"<SYMBOL>": {"direction_from": "Buy|Sell", "comment": "..."}}`.
- Триггер: `markPrice >= breakEvenPrice × (1 + TRIGGER_BUFFER_PCT)` для Long (0.05% запас сверх BE).
- Flow: clear position TP/SL → market order `2×size opposite` (one-way flip) → найти ближайший support/resistance из detect_levels(D) → TP с RR≥3 (fallback entry-3×SL_dist) → set_trading_stop → TG-уведомление.
- State: `/var/lib/gerchik/auto_flips.json` — `{symbol: "done"}`, чтобы не повторить после рестарта.

## Текущие кандидаты (2026-05-19):
- `XRPUSDT`: Long 1.3797 → Short при mark ≥ 1.3826 (BE=1.382 + 0.05%).

## Where it hooks in:
- `src/main.py` main loop вызывает `auto_flipper.maybe_flip(bybit)` на каждой итерации.
- TG-уведомление: `send_level_notification(level_id=-1, level_type="auto_flip", ...)` с полным блоком RR/Grade/HTF.

## Manual flip пример (BNB 2026-05-19):
Сделан inline-скриптом не через auto_flipper — был ad-hoc. Sell 0.16 market → Short 0.08 @ 639.2, SL=653.6, TP=591.8, RR=1:3.29. TG msg_id=70.

## Связанные:
- [[feedback_agent_levels_guards]] — те же RR/SL/TP правила для consistency.
- [[project_bybit_3sub_architecture]] — выполняется на sub3 (AI agent).
