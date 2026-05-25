---
name: session-2026-05-21-tp-redesign
description: "2026-05-21 переход всех 3 стратегий на 100% close на TP1=2R + BE off на CONS/TREND + EMA Gate 1H/200 on. Reasoning, метрики до, что мониторить дальше."
metadata: 
  node_type: memory
  type: project
  originSessionId: cbd11597-bb85-4f31-a1c0-60ce301b7c11
---

**Контекст:** Артём прислал скрин dashboard'а со статистикой 3 стратегий (CONS/TREND/AGGR), все 3 в paper-mode, все 3 в минусе (−$110/−$118/−$97). Просил «не предлагать повышение spike — бесполезно». Задача — посчитать математику и предложить настройки в плюс.

**Корневой анализ:**
- На CONS из 97 TP1 trigger'ов 96 retraced в BE → партиал даёт средний винер $0.42 при среднем лузере −$0.93. PF 0.20–0.28 во всех стратегиях.
- 5-уровневая лесенка не работает: TP2 hit 0.4–1.9%, TP3+ почти нули.
- При 100% close на TP1=2R математика выходит в плюс: AGGR +$108 gross на тех же сигналах (124×2 − 140 = +108), CONS/TREND ~+$30/+$10.

**Что изменили (paper, все 3 strats, через `/api/settings`):**
- `tp_distribution`: CONS [0.33/0.33/0.33] → [1.0/0/0]; TREND [0.20×5] → [1.0/0/0/0/0]; AGGR [0.22/0.28/0.22/0.17/0.11] → [1.0/0/0/0/0]
- `tp_ratios[0]`: CONS 1.1R → 2.0R; TREND 1.5R → 2.0R; AGGR уже 2.0R (не трогали)
- `be_activation_pct`: CONS 0.46% → 20% (≈off); TREND 0.8% → 20% (≈off); AGGR 1.5% не трогали
- **Update 2026-05-21 ~19:00 UTC:** Артём руками выставил 3 разных BE-конфига как A/B/C-эксперимент: CONS 1.6/0.6, TREND 1.8/0.8, AGGR 1.5/0.5. См. [[project-be-per-strategy-experiment]] — НЕ трогать минимум 30 дней.
- `ema_gate.enabled`: false → true (tf=60, period=200, hot-reload)
- Сделан рестарт `bybit-tradingbot`. Уже открытые 17 позиций на момент рестарта доедут со старыми DB-уровнями — это нормально.

**Why:**
- Текущий setup физически не мог быть прибыльным: партиалы съедали виннеры, BE-offset 0.15% превращал TP1-touch в scratch. Память: [[feedback-funnel-vs-close-reason]].
- 2R даёт break-even при WR=33% — все 3 стратегии его уже бьют по TP1 hit-rate.
- EMA Gate — самый дешёвый фильтр (hot-reload, no restart), которым нужно было давно включить.

**How to apply / следующие шаги:**
- Мониторить 24–48ч через v2-dashboard. Целевые метрики: WR ≥ 33% на 2R, PF > 1, net > 0 across 50+ closes per strategy.
- Если WR < 30% после EMA Gate — значит сигналы шумные сами по себе, тогда B/S ratio 1.5 → 2.0, time-of-day filter, агрессивный auto-BL.
- Открытое TODO: shadow ladder для мониторинга «куда могла дойти цена выше TP1=2R» — см. [[project-tp-shadow-ladder]].
- Запретили: ещё одно повышение spike_ratio (Артём явно сказал «бесполезно»).

**Файлы тронуты (через dashboard, не руками):**
- `config/trading_v3_artem.json` (strategy_parameters.{conservative,trend,aggressive}.tp_ratios + tp_distribution + be_activation_pct)
- `src/signal_bot_config.json` (ema_gate.enabled=true)
- `bot_settings` (зеркалится через SETTINGS_REGISTRY apply chain — см. [[project-dashboard-apply-chain]])
