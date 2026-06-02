---
name: feedback-manual-close-mislabeled-tp1
description: ручное закрытие прибыльной real-позиции reconciler помечает как TP1 — релейблить в MANUAL чтобы не пухла TP-воронка
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 46f870fa-7970-491c-8823-c7cddf59890d
---

Когда Артём вручную закрывает прибыльную real-позицию на Bybit, фоновый reconciler (`order_executor_wrapper_v3._infer_close_reason`) видит только `closedPnl>0` и exit в сторону профита → штампует `close_reason='TP1'`/`close_source='bybit_tp'`. Отличить ручной market-close от TP-fill по Bybit-данным нельзя.

**Why:** такой выход часто далеко за TP1 (напр. FARTCOIN 2026-06-01: SHORT entry 0.16461 → manual exit 0.15033 = +8.68%, +$6.79, тогда как TP1=0.6%≈0.16362). Залетев в TP1-бакет, он раздувает TP-воронку, avg-TP1-win и R-метрики (типичный TP1 ~$1.66).

**How to apply:** после ручного закрытия — найти строку `real_trades` (по symbol+entry_time, is_shadow=false), проверить exit_price vs TP1, и если это ручной выход — `UPDATE real_trades SET close_reason='MANUAL', close_source='manual_close', tp1_triggered=false WHERE id=...`. Цифры (realized/gross/fees/exit) reconciler берёт из Bybit closed-pnl — они верные, трогать только лейбл. MANUAL не входит ни в один funnel-бакет (TP/BE/SL/FORCE), но считается в WR/net — это и есть честная трактовка. Связано с [[project-trading-critical-params]] §10, [[feedback-real-trades-fee-semantics]].
