---
name: feedback-ga-unrealistic-tps
description: "GA рекомендует TP в космосе (13R-48R), хотя реальная MFE доходит максимум ~2%; backtester засчитывает wick-касания на 5m, реал так не работает"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

GA-оптимизатор регулярно выдаёт TP-ratios 13-48R хотя по реальной MFE ни одна позиция дальше ~2% не уходит. Артём отверг 2026-05-13 как «бред».

**Why:** GA backtester держит позицию до TP или SL без time-stop и считает fill любое касание уровня wick'ом 5m-свечи. На большой выборке (~13k trades) GA находит wicks которые ловят даже 48R-уровень — для fitness это +EV, для реала эти trades никогда не закрываются на TP.

**How to apply:**
- Прежде чем рекомендовать или применять GA-кандидата — **всегда сверять TP-ratios с реальной MFE distribution** (`peak_pnl_pct` из simulated_trades / реальных trades).
- Если рекомендованный TP > 95-99 перцентиля MFE по соответствующей стратегии — это **mirage**, не применять.
- Починка GA должна включать MFE-cap на TP-ratios (constraint в decode_genome) ИЛИ time-stop в backtester ИЛИ оба.
- Артём сейчас на грани отказа от GA — каждый бессмысленный прогон тратит его время; не запускать новые GA без явного запроса.
- Связано с [[project-ga-walk-forward-todo]], [[project-ga-realism-overhaul]], [[project-mfe-mae-tracking]] — следующая итерация realism должна использовать MFE-данные.
