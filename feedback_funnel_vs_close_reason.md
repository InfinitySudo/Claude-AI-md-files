---
name: feedback-funnel-vs-close-reason
description: "TP Funnel cells = trigger events (overlap), а не разбиение closed-trades; сумма funnel'а > closed нормально, mutually exclusive — только close_reason"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

В дашборде v2 «TP Funnel» под каждой strategy-карточкой Артём прочёл как «разбиение закрытых сделок» — сумма ячеек > closed-count его смутила (CONS: 758 closed, но funnel 1263 событий).

**Why:** Каждая funnel-ячейка считает trades, у которых соответствующий trigger-flag (`tp1_triggered`, `tp2_triggered`, `tp3_triggered`, `be_triggered`, `sl_triggered`) был true хотя бы раз. Один и тот же trade может оказаться в TP1 (частичное закрытие) И в BE (откат к BE-стопу на остатке) одновременно — это норма для TP-ladder + BE-trailing стратегий. Mutually exclusive разбиение даёт **только** `close_reason` (BE / SL / TP-final), и его сумма точно равна `COUNT(*) WHERE status='closed'`.

**Пример CONS на 2026-05-13:**
- closed: 758
- close_reason: BE 381 + SL 336 + TP3(c) 41 = **758 ✓**
- tp1_triggered: 443 (из них 381 потом откатились к BE, 11 в SL, 41 доехали до TP3, 10 ещё open)
- funnel sum: 443 + 62 + 41 + 381 + 336 = 1263

**How to apply:**
- Любой UI с overlap-counters'ами должен **явно** говорить «trigger events / cells overlap» (как теперь в `funnel-title` после коммита 6fb2988). Без этого пользователь считает сумму и не сходится.
- Если показываешь mutually-exclusive разбивку — используй `close_reason`, не флаги.
- В отчётах/SQL для «сколько % сделок дошли до TP3 как final» = `COUNT WHERE close_reason LIKE 'TP3%'`, а не `COUNT WHERE tp3_triggered`.
- Связано с [[feedback-reports-win-rate]] (WR = money-based, не TP-rate), [[feedback-real-trades-truth]] (real_trades иногда лжёт по флагам).
