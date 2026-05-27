---
name: real-topup-2026-05-18
description: "Артём планирует пополнить Bybit (sub1, TradingBot) до круглых $100 для CONS-real после чистого старта fan-out"
metadata: 
  node_type: memory
  type: project
  originSessionId: 49ea4545-bbbc-4b86-b277-32955052d57f
---

**2026-05-18 ~23:11 UTC** — после force-close всех open positions (real CONS + paper TREND/AGGR) и рестарта бота для чистого А/B/C-эксперимента fan-out, wallet был **$93.47**. Артём сказал: «пополню счёт до целых $100 для CONS real, отметь себе».

**Why:** старт fan-out (1 signal → CONS real + TREND paper + AGGR paper) идёт с этого момента. Round-number baseline нужен чтобы PnL-сравнение и DD-метрики читались чище.

**How to apply:**
- Когда Артём подтвердит что transfer выполнен — обновить `bot_settings.session_start_wallet_usd` на новую сумму ($100 ровно). Иначе total_DD-guard будет считать просадку от старой baseline 99.86 + не учтёт top-up.
- Memory `[[session-baseline-transfers]]` уже описывает что transfer ловит DD guard как просадку → нужно сбросить baseline после пополнения.
- Запрос на сброс: `POST /api/dd/ack-session-start` (если такой endpoint есть) или прямой UPDATE `bot_settings.session_start_wallet_usd = <new_balance>`.
- Проверить также `bot_settings.transferred_out_manual_usd=150` — это **выведенные** ранее средства, не возврат. Не путать.

См. [[session-baseline-transfers]], [[real-trades-baseline]].
