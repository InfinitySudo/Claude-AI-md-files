---
name: agent-levels-tg-dedup
description: "gerchik-trading-agent — любой новый caller place_level() ОБЯЗАН использовать tg_notified_at gate перед send_level_notification, иначе TG спамится дублями."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9852af16-b727-436e-bcef-2fb1ec5f5cc9
---

В `gerchik-trading-agent/src/agent_levels.py:place_level()` есть idempotent-семантика: для уже активного уровня возвращается **truthy existing id**, а не `None`. Это значит проверка `if level_id:` НЕ отличает новый INSERT от re-fetch'а. Любой caller, шлющий TG-уведомление сразу по level_id, будет спамить одним и тем же уровнем каждый часовой `maybe_refresh` (TTL=3600s) — Артём ловил 4-5 дублей одного BTC/ETH уровня 2026-05-19.

**Why:** `place_level` дедуплицирует ордер на Bybit (`orderLinkId` hash) и DB-row (UNIQUE constraint по `(symbol, side, ROUND(price,8), source, status IN pending/placed)`) — но контракт возврата id оставлен «idempotent» специально, чтобы caller мог получить ссылку на текущий level даже на reattempt. Поэтому TG-dedup ОБЯЗАН быть на стороне caller'а, не в `place_level`.

**How to apply:** перед `send_level_notification(...)` всегда делай атомичный claim:
```python
claim = _DB().query_one(
    "UPDATE agent_levels SET tg_notified_at=NOW() "
    "WHERE id=%s AND tg_notified_at IS NULL RETURNING id",
    (level_id,),
)
if not claim:
    continue  # уже нотифицировали — пропустить
```
Reference impl: `signal_engine.py:_sync_agent_levels` (commit `50ab93f`, migration `013_agent_levels_tg_notified.sql`). `auto_flipper.py` шлёт с `level_id=-1` — для него нужен ДРУГОЙ механизм dedup (он сам управляет state через `_save_state`), `tg_notified_at`-гейт там не работает.

См. [[trading-spec]], [[bybit-3sub-architecture]].
