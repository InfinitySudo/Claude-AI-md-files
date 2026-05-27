---
name: clean-start-snapshot-2026-05-18
description: "Полный snapshot всех настроек dashboard на момент чистого старта fan-out эксперимента (CONS-real, TREND-paper, AGGR-paper)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 49ea4545-bbbc-4b86-b277-32955052d57f
---

**2026-05-18 23:30 UTC** — после force-close всех open позиций (10 real + 4 paper) и рестарта fan-out, Артём попросил «сделать snapshot всех настроек и запомнить в удобное место».

**Где живёт**: `4BotsBybit-Trading/scripts/snapshots/clean_start_2026_05_18.json` (~13 KB, 509 строк).

Содержит:
- `bot_settings` (вся таблица — 45+ ключей включая SETTINGS_REGISTRY-managed: `hybrid_baseline_at=2026-05-18 23:14 UTC`, `strategy_mode=AUTO`, `forced_strategy=CONSERVATIVE`, `atr_multiplier=0.25`, `leverage=80`, `be_activation_cons/trend/aggr`, `be_offset_*`, `*tp*_R`, `*_tp*_close`, `signal_volume_usd=300000`, `signal_spike_ratio=5`, `ema_gate_*`, `anti_fade_*`, drawdown thresholds, риски, ML/risk-officer toggle, GA params).
- `trading_v3_artem.json` (полный JSON-конфиг: `trading_mode.per_strategy` hybrid map, `strategy_parameters.{cons,trend,aggressive}` с актуальными tp_ratios после fan-out).
- `signal_bot_config.json` (signal criteria + EMA-gate config).

**Why:** точка отката для эксперимента fan-out + A/B/C-сравнения трёх стратегий с разными параметрами. Если параметры сдвинутся и результаты ухудшатся — этим snapshot'ом можно восстановить starting state.

**How to apply:**
- Восстановление настроек: распарсить JSON, для каждого `bot_settings.<key>` POST на `/api/settings/<key>` (если ключ в SETTINGS_REGISTRY) либо ручной UPDATE bot_settings. Для `trading_v3_artem.json`/`signal_bot_config.json` — через `/api/settings` (dotted-path keys в SETTINGS_REGISTRY) или прямая запись JSON (но первый путь предпочтительнее, см. CLAUDE.md).
- Anti-pattern: НЕ перезаписывать оба JSON-файла целиком, потому что в них есть live-state (например `applied_at`, `applied_by`) который не должен откатываться.
- Перед массовым apply — стопнуть bot чтобы хот-релоад не подхватил частичное состояние.

**Связанное:**
- [[real-topup-2026-05-18]] — Артём планирует пополнить wallet до $100, тогда session_start_wallet_usd тоже надо будет обновить.
- [[hybrid-mode]] — описывает per_strategy routing.
- [[trading-mode-routing]] — как trading_mode.per_strategy управляет paper/real маршрутом.
- [[fanout-architecture-2026-05-18]] — описание fan-out (1 signal → 3 strategy-trades).
