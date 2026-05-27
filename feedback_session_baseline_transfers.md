---
name: session-wallet-baseline-traps-wallet-transfers
description: "Drawdown guard сравнивает live wallet с `session_start_wallet_usd` — любой sub-account transfer / withdraw читается как просадка и блокирует ордера"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f4c4861-fd60-4f57-b7af-c4260e03075c
---

`main_bot_v3._check_total_drawdown` блокирует все сигналы когда
`(session_start - current) / session_start ≥ total_max_drawdown_pct`
(default 15%). Baseline хранится в `bot_settings.session_start_wallet_usd`,
сидится при первом запуске и НЕ обновляется автоматически.

**Why:** 2026-05-15 — переключили бота в full REAL после $150 transfer на
sub-accounts. Equity $189.60 → $61.52 (mathematic DD 67.55%). Guard
блокировал все два первых REAL-сигнала (SKYUSDT и ещё один) с
`🛑 BLOCKED by cumulative drawdown guard: Total session DD 67.55% ≥ 15.0%`.
Никаких real-сделок до этого не было, статистика real_trades осталась
нулевой. Дашборд показывал "paper (pending real)" в карточках, что и
ожидалось.

**How to apply:**
- Любой выход денег (transfer на sub, withdraw, ручной debit) → СРАЗУ
  `UPDATE bot_settings SET setting_value=<new_balance> WHERE
   setting_name='session_start_wallet_usd'`.
- То же при пополнении кошелька — baseline можно поднимать чтобы DD
  считался от нового уровня (иначе guard будет «спать» пока не съест
  весь излишек).
- При свитче mode PAPER→REAL после длинной paper-сессии — проверять
  baseline ДО первого ордера, не после.
- `system_baseline_v2_wallet` — отдельный snapshot для дашборд-метрик,
  не для guard'а; синхронизация не обязательна.

Связанное: [[project_trading_state_softgate]], [[feedback_dd_guard_paper_skip]].
