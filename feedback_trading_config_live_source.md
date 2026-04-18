---
name: Trading Config Live Source
description: Never assume GA-applied values are still live — Artem retunes via dashboard; always query actual state
type: feedback
originSessionId: a080f8b3-13b0-4be7-8650-c581d878ad77
---
Артём регулярно правит trading params через дашборд (Settings tab) напрямую, независимо от GA-оптимизатора. GA #1, применённый 2026-04-13, к 2026-04-18 уже перезаписан (tp_ratios, atr_multiplier, spike_threshold, max_positions — всё другое).

**Why:** GA даёт отправную точку, но Артём tuned вручную после наблюдений в проде. Доверять памяти о "текущем конфиге" опасно — быстро устаревает.

**How to apply:** При любом анализе позиций/поведения бота — ВСЕГДА сначала читай актуальные значения:
- `config/trading_v3_artem.json` → `strategy_parameters.{conservative,trend,aggressive}.tp_ratios/tp_distribution`
- Таблица `bot_settings` в Postgres → `atr_multiplier`, `spike_threshold`, `leverage`, `risk_per_trade`, `max_positions`, `tp1..5_percent`
- Обе точки — dashboard пишет в одну или другую, нужно смотреть обе

Никогда не цитируй значения из памяти как "текущие" — только как исторический снимок с датой.
