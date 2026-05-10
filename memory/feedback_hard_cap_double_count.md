---
name: HARD CAP двойной счёт + вид open paper в dashboard
description: max_position_usd_per_symbol режется через position×leverage; dashboard hardcoded forced_real игнорирует JSON per_strategy
type: feedback
originSessionId: 93067773-cafa-4ab3-b8c6-cf84bdc85eda
---
## HARD CAP в risk_manager_v3.py

`position_size_usd = qty_coins * entry_price` — это **уже контрактная стоимость** (=Bybit "Order value"), не margin.

Старая формула `notional = position_size_usd * applied_leverage` делала двойной счёт. С cap=$50 и leverage 80x: позиция $70 контракта × 80 → $5600 fake notional → scale ×0.009 → финальный qty × price = $0.62. Ниже Bybit min $10 → **ВСЕ TREND/AGGRESSIVE сигналы тихо отбивались** биржей.

**Why:** `position_size_usd` — historical legacy name; буквально USD-стоимость контракта. `applied_leverage` определяет только **margin requirement** = position / leverage, не notional.

**How to apply:** при любом изменении risk_manager_v3.py всегда проверять — переменная `notional` должна равняться `qty × entry`, **не** `qty × entry × leverage`. Переменная `margin` = `notional / leverage` (если когда-нибудь добавим).

Fix 2026-05-09: убрал `* applied_leverage` в строке 395; cap теперь прямо ограничивает контрактную стоимость.

## Dashboard `_v2_resolve_source` — забывал про live JSON

Хардкодил `STRATEGY_V2['forced_real']=True` для TREND/AGGR и читал `real_trades_compat`. Когда Артём переключал `per_strategy.TREND` в `trading_v3_artem.json` на PAPER, dashboard всё равно тянул из real_trades → open paper-сделки **не были видны** на `/api/v2/strategy/<name>`.

Fix 2026-05-09: `_v2_resolve_source` читает per_strategy из JSON на каждый вызов. PAPER → simulated_trades, REAL+есть rows → real_trades, REAL+пусто → paper_pending_real, JSON broken → fallback на legacy hardcode.

**How to apply:** любой код в dashboard_api_v3.py что выбирает источник (paper vs real, simulated_trades vs real_trades_compat) ОБЯЗАН читать живой `trading_v3_artem.json`/`bot_settings`, не доверять `STRATEGY_V2[]['forced_real']`. Хардкод должен быть только в fallback-ветке.

## Связано

- Сигналы в TG приходят, но `signals_queue` -> trader отбивает: проверять `journalctl -u bybit-tradingbot | grep -E "HARD CAP|REJECTED|Order value"` — там видно blacklist, hard cap, или min order check.
- Если open paper-сделка не видна на dashboard но есть в `simulated_trades WHERE status='open'` — это `_v2_resolve_source` баг рецидив.
