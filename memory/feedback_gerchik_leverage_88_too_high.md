---
name: gerchik-leverage-88-too-high
description: real_leverage 88× в gerchik душит scanner через liquidation_buffer filter; снижено до 35× 2026-05-12; ожидается рост частоты signals на Layer 1
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e259f10c-4218-4b83-a0fd-cb861ccaa1f1
---

**Не возвращай real_leverage обратно к 88× без переписывания liquidation_buffer.**

**Why:** В config/gerchik_config.json стояло `real_leverage: 88` (Phase 2 с 2026-05-10). signal_engine.py фильтр #7 (`check_liquidation_buffer`) требует SL ближе entry чем liquidation на ≥0.5%. С 88× liq на ~1.1% от entry → SL должен быть ≤0.6% от entry. На 1H reversal-паттернах при ATR_5D BTC ~$1500 минимальный реальный SL = 0.8-1.5% → всегда дальше liq → filter отбивает. За 36 часов native scanner нашёл 1 сетап на 5 majors. После снижения до 35× (liq ~2.85% от entry, SL до 2.3% помещается) ожидается порядок больше signals.

**How to apply:**
- Если Артём захочет вернуть высокий leverage — сначала переписать `check_liquidation_buffer` или сделать его per-symbol soft.
- В config: `real_leverage_overrides = {}` (BNB max 50× теперь >35×, override не нужен).
- gerchik-agent service подхватывает конфиг ТОЛЬКО на рестарт; всегда `systemctl restart gerchik-agent` после правки.
- Фактический Bybit-leverage выставляется per-trade через `set_leverage()` в момент open_real — open позиции с 88× НЕ пересчитываются автоматически.

Связано с [[gerchik-trading-agent]] и [[real-trades-truth]].
