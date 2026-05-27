---
name: pyramid-fix-gerchik-trading-agent
description: "gerchik-trading-agent: one row per (symbol, mode) — add-on entries aggregate into the open row via weighted-avg, not separate rows. Fix for 2026-05-16 PnL inflation bug."
metadata: 
  node_type: memory
  type: project
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

`/root/gerchik-trading-agent/` (sub3 AI-agent) since 2026-05-16 (commit `dbea126`).

## Контракт

- **На (symbol, mode) только ОДНА row** со `status='open'` в `gerchik_trades`. Никогда не вставляй вторую — append into the open row.
- `journal.get_open_trade_on_symbol_mode(db, symbol, mode)` → row dict | None — used by routing.
- `journal.append_to_open_trade(db, trade_id=..., added_qty, added_entry, bybit_order_id, added_risk_usd)` — updates `qty (sum)`, `entry_price (weighted avg)`, `bybit_order_ids (comma-append)`, `risk_usd (sum)`, `add_on_count += 1`.
- `journal.has_open_on_symbol(db, symbol, mode=None)` — `mode=None` scans **both** PAPER+REAL. Pass `mode='REAL'` или `'PAPER'` explicitly для scoped check.

## Routing в `signal_engine.evaluate()`

```
target_mode = 'REAL' if symbol in real_symbols else 'PAPER'
existing = get_open_trade_on_symbol_mode(symbol, target_mode)

if existing:
    if add_on_count >= MAX_ADD_ONS (=3): skip
    if direction != existing.direction: skip (no reversal pyramid)
    if target_mode == 'REAL':
        order_id = real_executor.append_real(qty)  # market order, Bybit aggregates One-Way
        journal.append_to_open_trade(...)
    else:
        journal.append_to_open_trade(...)  # paper: DB only
    return

# block cross-mode coexistence
if journal.has_open_on_symbol(symbol):  # other mode is open
    skip

# fresh entry
open_real(...) or open_paper(...)
```

## Колонки на `gerchik_trades` (после migration 011)

- `bybit_order_id` — initial entry order_id
- `bybit_order_ids` — comma-separated chain (initial + all add-on order_ids)
- `add_on_count` — int, increments per append
- `first_entry_price` — immutable initial entry (vs `entry_price` = current weighted avg)
- `updated_at` — auto-touched при append

## Что важно знать чтобы не сломать

- `real_executor.open_real` пишет `bybit_order_id` при первом insert через `journal.open_trade(..., bybit_order_id=...)`.
- `real_executor.append_real(bybit, symbol, direction, qty, leverage)` НЕ трогает journal — caller wraps. Returns order_id.
- Add-on **не пере-attach TP/SL** — Bybit position-level держит существующие stops на aggregated qty.
- Paper add-on: signal_engine вызывает `journal.append_to_open_trade` напрямую (no paper_executor.append_paper нужен).

## Что НЕ делать

- Не возвращать default `mode='PAPER'` в `has_open_on_symbol` — это был root cause бага.
- Не использовать `open_trade()` для add-on'ов — duplicate row кидать.
- Не вводить reversal-pyramiding (LONG add-on на SHORT-position) — Bybit One-Way это запутает; направление должно совпадать.

## Тесты

`tests/test_pyramid_routing.py` — 7 кейсов:
1. `has_open_on_symbol` без mode видит REAL trade (regression test для багa)
2. `has_open_on_symbol` с explicit mode scoped правильно
3. append: 100@1.46 + 50@1.47 → 150@(weighted avg), count=1
4. append no-op если trade не open
5. `get_open_trade_on_symbol_mode` возвращает row
6. `get_open_trade_on_symbol_mode` возвращает None для другого mode
7. `open_trade` записывает `first_entry_price` и `bybit_order_id`

`MAX_ADD_ONS_DEFAULT = 3` (в `signal_engine.py`) — total entries cap = 4 per position.

## Backfill старых rows

**НЕ делается**. 6 XRP-rows от 2026-05-14 остаются в DB как paper history. Stream B на дашборде уже идёт из Bybit closed-pnl truth (не из DB), так что user view не врёт.

## Verification после рестарта

```bash
systemctl restart gerchik-agent
# При следующем pyramid signal в логах:
#   "➕ XRPUSDT LONG REAL add-on #1: qty +X @ $Y order=byb_id..."
# В DB:
psql -d trading_bot_v3 -c "SELECT trade_id, qty, entry_price, add_on_count, bybit_order_ids FROM gerchik_trades WHERE status='open'"
# → одна row, add_on_count >= 1, qty/entry увеличены, bybit_order_ids = "a,b,c..."
```
