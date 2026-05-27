---
name: be-on-real-must-use-bybit-avgprice-not-signal-entry
description: "Critical bug 2026-05-15. Computing BE-SL from row['entry_price'] (=signal) instead of live_pos.avgPrice (=actual fill) locks slippage as guaranteed loss on every trade with unfavourable fill. Cost ~$13 in 7h of first real trading."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f4c4861-fd60-4f57-b7af-c4260e03075c
---

В `OrderExecutorWrapper._maybe_move_be_real` (`order_executor_wrapper_v3.py`) — **ВСЕГДА** брать entry price из `live_pos.get('avgPrice')`, не из DB row. Только если `avgPrice` отсутствует, fallback на `row['entry_price']`.

```python
entry = float(live_pos.get('avgPrice') or 0) or float(row.get('entry_price') or 0)
```

**Why:** DB `entry_price` это **signal price** (что мы попросили у Bybit как лимит/маркет), `live_pos.avgPrice` это **actual fill** (что Bybit реально дал). При slippage в плохую сторону (LONG fill выше signal, SHORT fill ниже) BE-SL рассчитанный от signal попадает **внутрь slippage gap** → mark при первом дёрге пробивает его → close at near-signal, net = slippage + fees = guaranteed loss.

Real example 2026-05-15 ADAUSDT id=27:
- signal_entry 0.2604, actual fill 0.2609 (+0.19% slippage)
- BE-SL set @ 0.2606604 = signal × 1.001 ← НИЖЕ actual fill
- Mark drift к 0.2604 → SL filled → net −$0.28 (slippage + fees)
- 22 из 28 первых real trades follow same pattern, all labelled close_reason='SL' но фактически это false-SL (exit ≈ signal_entry, не близко к ATR-based sl_price).

**How to apply:**
- Любая логика которая использует "entry" для **trading-side decisions** (SL placement, BE-move, partial close levels) → читать `live_pos.avgPrice` через Bybit API/get_open_positions
- Для **reporting** (charts, dashboard, slippage_pct stat) → можно сравнить signal vs avgPrice (это и есть slippage measurement)
- Регресс-тест: `tests/test_reconciler.py::test_be_uses_live_avg_price_not_signal` — asserts BE-SL > actual fill для LONG → block reverse-bug.

Fixed in commit ff503ef (2026-05-15).

Связано: [[project_hybrid_mode]], [[feedback_real_trades_truth]] (DB врёт по PnL — здесь же DB врёт по entry), [[project_mfe_calibration]].
