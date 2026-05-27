---
name: project-real-trades-consolidation-done
description: 2026-05-24 одношот consolidation 25 phantom real_trades rows → 7 master + 12 CONSOLIDATED + 6 ORPHAN_RECONCILED. Script scripts/consolidate_real_aggregated_rows.py (commit d349d6a) — для будущих случаев если dup-check сломается снова.
metadata: 
  node_type: memory
  type: project
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

## Что было
До commit 631dd30 (dup-check global guard для REAL) AGGR-real re-entry'ил на одну Bybit-aggregated позицию по несколько раз. На 2026-05-24 в `real_trades.status='open'` сидело 25 фантомных rows в 9 группах:
- SUIUSDT × 5, DOGE × 4 (orphan — на бирже уже нет), LINK × 3, XRP × 3, STRK × 2 (partial closed), 1000PEPE/ETH/FARTCOIN/LTC × 2.

## Что сделано
`scripts/consolidate_real_aggregated_rows.py` (одноразовый, dry-run-by-default):
- **Category A** (Bybit live qty ≈ sum DB qty): newest row → master с qty/SL от Bybit + weighted-avg entry. Остальные → `status='closed', close_reason='CONSOLIDATED', realized_pnl_usd=0`.
- **Category B** (Bybit qty < sum DB qty, partial closed): то же что A.
- **Category C** (Bybit нет позиции): все rows → `close_reason='ORPHAN_RECONCILED'`.

Backup перед apply: `pg_dump -t real_trades > data/backup_real_trades_pre_consolidation_20260524_1111.sql`.

Результат: 25 rows → 7 master kept + 12 CONSOLIDATED + 6 ORPHAN_RECONCILED. `real_trades.open`: 43 → 25 (matches 20 live Bybit pos + 5 already-singleton).

## Когда переиспользовать
Если dup-check global guard когда-нибудь сломается (например, при переходе на multi-strategy real per [[project-real-global-guard-limitation]]) — script готов, просто запустить:
```
python3 scripts/consolidate_real_aggregated_rows.py            # dry-run
python3 scripts/consolidate_real_aggregated_rows.py --apply
```

## Известное искажение headline после consolidation
- `closed_count` вырос (CONSOLIDATED+ORPHAN считаются closed)
- `realized_pnl=0` для них → не влияет на total P&L
- Bybit cross-check может расходиться с DB net на сумму orphan'ов (на бирже у них был реальный PnL, в DB обнулен).

Связано: [[project-real-global-guard-limitation]], [[feedback-orphan-residual-recovery]].
