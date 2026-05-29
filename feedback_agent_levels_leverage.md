---
name: feedback-agent-levels-leverage
description: "agent_levels.place_level раньше не выставлял плечо → биржа держала стейловые значения (ETH 10x, BTC 88x); теперь форсит из gerchik_config.json"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 520ebb72-e212-4d77-8428-d58bac900b5b
---

В `/root/gerchik-trading-agent` ДВА торговых пути с разной историей по плечу:
- `real_executor.py` (open_real/append_real) — **всегда** звал `set_leverage` (строки 116/204).
- `agent_levels.py:place_level` (AI-уровни на sub3, `source='ai'`) — **НЕ трогал плечо** → Bybit использовал last-set per-symbol значение. Итог 2026-05-29: ETH висел на 10x, BTC на 88x, хотя `config/gerchik_config.json` → `real_leverage: 35`.

**Why:** из-за 10x ETH-шорт держал лишнюю маржу, а 88x BTC давал близкий liq. Плечо рассинхронилось молча, конфиг не форсился.

**How to apply:** fix 2026-05-29 — добавил параметр `leverage` в `place_level`, вызов `bybit.set_leverage(symbol, leverage)` перед `place_limit_entry` (идемпотентно: retCode 110043 = success). `signal_engine.py:136` передаёт `self._leverage_for(symbol)` (учитывает `real_leverage_overrides`). Применяется только при постановке НОВОГО уровня; existing-active уровни скипаются, поэтому при разовом дрейфе ровнять руками: `set_leverage` по всем `real_symbols`. qty в place_level — notional-based ($50 MARKER_QTY_USD), плечо на qty не влияет, только на маржу/liq. Связано с [[feedback-agent-levels-cooldown]], [[feedback-agent-levels-sl-atr]].
