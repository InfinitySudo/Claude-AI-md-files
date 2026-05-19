---
name: project-ga-under-review
description: "GA на грани отказа 2026-05-13 — выдаёт нереалистичные TP, тратит время; решение fix-vs-kill pending"
metadata: 
  node_type: memory
  type: project
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

**Статус 2026-05-13:** Артём недоволен GA — после Phase 1-4+2.5 realism overhaul + Walk-Forward + дашборд UI, GA всё ещё выдаёт TP=13-48R, нереалистичный spike_ratio=10.8 и т.п. Считает что GA скорее мешает, чем помогает.

**Why:** Несколько недель работы (см. [[project-ga-realism-overhaul]], [[project-ga-walk-forward-todo]], [[project-baseline-v2-2026-05-08]]) не сделали GA полезным. Backtester игнорирует реальную MFE distribution (макс ~2%), Sharpe-cap защищает fitness но не TP-плейн. Артём предпочёл бы вручную править стратегию по графикам/статистике.

**How to apply:**
- НЕ запускать новые GA-прогоны без явного запроса.
- При работе со стратегией предлагать manual-tuning от MFE/MAE и hourly_report анализа, а НЕ GA.
- Если решено **чинить**: следующие шаги в [[feedback-ga-unrealistic-tps]] (MFE-cap на TP, time-stop в backtester, sanity-check apply).
- Если решено **выпиливать**: отключить cron Sun-night GA, скрыть GA-таб в дашборде, оставить код в репо как research-only.
- Связь: [[project-baseline-v3-2026-05-10]] (после wipe всё перезапущено заново — нет данных подтверждающих edge GA-настроек).

## 2026-05-18 — GA paused: накопить real-данные перед следующим прогоном

Артём решил: **выключить автоматический GA-прогон** до накопления достаточной real-выборки. UI показал Sharpe(test) 47, P&L(test) +$6656 — нереально (на real PF 0.93). Причины: paper-симулятор оптимистичен (видели paper +$324 vs real −$17 на одинаковом периоде), walk-forward 70/30 train/test не помогает потому что оба окна paper, TP-ratios типа 6.26R не достигаются в реале.

**Действия выполнены:**
- `bot_settings.ga_weekly_enabled = false` (direct DB update, updated_by='manual_ga_pause_2026_05_18'). Cron на Sunday 23:00 UTC больше не запускает GA.
- Ручной запуск через dashboard "▶ Run new GA" по-прежнему работает — не блокировал.

**План дальше:**
1. Копить real_trades после fan-out reset (2026-05-18 23:14 UTC). Цель: 100+ real trades per strategy × 3 strategies = 300+ post-baseline.
2. При накоплении — рефакторить GA fitness:
   - Train на real_trades (не simulated), test на out-of-sample real.
   - MFE-guarded TP-cap: TP ≤ p90(real peak_pnl_pct).
3. Включить `ga_weekly_enabled = true` обратно только после доказанного MFE-calibration + честный backtest.

**Альтернатива/replacement сейчас:** **MFE-калибровка** (`/api/mfe/calibration`) — берёт actual peak_pnl_pct из real-сделок, не симулирует. Это честнее backtest'а: см. dashboard MFE tab + memory [[mfe-calibration]].
