---
name: force-bucket-close-source
description: "real_trades.close_reason has 5 values now: TP{N}/SL/BE/LIQ/FORCE. close_source column tracks classification origin. FORCE = not real Bybit-SL hit."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

Since 2026-05-16 (commit `02b1cd0`) `_infer_close_reason` в `order_executor_wrapper_v3.py:660` возвращает **tuple `(reason, source)`** и close_reason имеет **5 buckets** вместо 4:

| close_reason | close_source | условие |
|---|---|---|
| `'SL'` | `'bybit_sl'` | chunk exit ∈ ±1% от sl_price |
| `'LIQ'` | `'bybit_liq'` | `execType` contains "bust" |
| `'BE'` | `'inferred_be'` | `|closed_pnl| < $0.05` |
| `'TP{N}'` | `'bybit_tp'` | pnl > 0, N chunks beyond entry direction |
| **`'FORCE'`** | **`'force_inferred'`** | **fallback**: pnl ≤ 0 AND no chunk near sl_price |
| (backfill) | `'force_inferred_backfill'` | retroactive relabel 2026-05-16 (46 historic SL rows where `|exit - sl| / sl > 1%`) |

## Why FORCE bucket existed раньше как ложный SL

До коммита `02b1cd0` fallback ветка `_infer_close_reason` возвращала `'SL'` для любого negative-pnl close без SL-chunk match. Это маскировало:
- BE-trail desyncs (Bybit-SL передвинулся на entry+0.1%, DB.sl_price остался ATR-distance)
- Manual close через Bybit UI
- Watchdog/script close
- High-slippage SL fills

70%+ "SL" в real_trades были такими false-positives. Backfill 2026-05-16 переразметил 46 строк из 76 SL → FORCE.

## Что важно знать

- **`sl_triggered = (reason == 'SL')`** — раньше было `startswith('SL')` что ловило FORCE. Теперь точное совпадение.
- **Auto-blacklist** (5-streak SL → 48h pause) использует `close_reason.upper().startswith('SL')` — НЕ ловит FORCE. То есть FORCE-streaks **НЕ** блокируют символ. По решению Артёма.
- **Strategy switcher** считает FORCE как loss (`LIKE 'SL%' OR = 'FORCE'`) — поведение свитчера сохранено.
- **Stats funnel** имеет FORCE как 3-й bucket (TP / SL / FORCE отдельно). WR_TP = TP / (TP + SL + FORCE).
- **BE-trail sync fix**: `_maybe_move_be_real` теперь пишет `sl_price = new_sl` в DB одновременно с `be_triggered=True`. Это устранило главный источник false-FORCE.

## Где видно на дашборде

- Strategy funnel: FORCE bar с оранжевым (`#fb923c`) border слева
- Excursion chips: `force_grazed_tp1` (FORCE peak ≥1%) и `force_clipped_green` (FORCE peak >0%)
- Drill-down modal: `close_reason='force'` filter поддерживается

## Backfill SQL

```sql
UPDATE real_trades
SET close_reason='FORCE', sl_triggered=false, close_source='force_inferred_backfill'
WHERE status='closed' AND close_reason='SL' AND sl_triggered=true
  AND sl_price > 0
  AND ABS(exit_price - sl_price) / sl_price > 0.01
  AND realized_pnl_usd <= 0;
```

(Применено 2026-05-16, 46 rows).

## Связано

- [[feedback-real-trades-truth]] — Bybit-as-truth, теперь содержит SL/FORCE split
- [[feedback-be-on-real]] — BE-trail mechanics; sync sl_price был ключевым fix
- [[feedback-real-trades-orphan]] — связанный паттерн manual recovery
