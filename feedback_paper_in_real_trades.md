---
name: feedback-paper-in-real-trades
description: "real_trades таблица содержала paper-trades CONS/TREND из hybrid-режима — false-tripped weekly DD guard. Чистка через archive+DELETE, не через ack-session-start."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: eeb6bcbc-09a2-4e37-b01a-7f90d2807f2c
---

В hybrid-режиме (CONS=paper, TREND=paper, AGGR=real до 2026-05-23) записи
CONSERVATIVE/TREND попадали в `real_trades` (видимо через
OrderExecutorWrapper с mock bybit_order_id). На 2026-05-23:
311 CONS + 26 TREND rows, net −$13.79 / −$14.48 → суммарный weekly
DD 31.07% ложно сработал и заблокировал AGGR через
`_check_cumulative_drawdown_guards()` (main_bot_v3.py:617).

**Why:** Сам guard читает только `real_trades` (строки 654-659),
формально корректно. Bug — в записи: paper-trades не должны были туда
попадать. Аналогично был BE-в-blacklist баг 2026-05-23.

**How to apply:**
- Если weekly DD guard срабатывает на «несуществующих» потерях — сразу
  SELECT по `real_trades` с фильтром по strategy/closed_at, сверить с
  фактическими сделками на Bybit (по bybit_order_id через `/v5/order/history`
  или `/v5/position/closed-pnl`).
- Reset через `POST /api/dd/ack-session-start` сбрасывает только
  `session_start_wallet_usd` (для TOTAL guard). Weekly guard **не имеет**
  endpoint'а сброса — чистится только через DELETE/исправление source-данных.
- Перед DELETE — всегда `CREATE TABLE real_trades_paper_archive_YYYYMMDD AS SELECT ...`.
- Архив 2026-05-23: `real_trades_paper_archive_20260523` (337 rows).

**Связано:** [[feedback_real_trades_truth]] · [[project_hybrid_mode]]
