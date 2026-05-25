---
name: project-be-per-strategy-experiment
description: "2026-05-21 — Артём руками выставил 3 РАЗНЫХ BE-конфига (CONS 1.6/0.6, TREND 1.8/0.8, AGGR 1.5/0.5) как параллельный A/B/C-тест. После 30+ дней данных выбрать «победителя» и унифицировать."
metadata: 
  node_type: memory
  type: project
  originSessionId: cbd11597-bb85-4f31-a1c0-60ce301b7c11
---

**Контекст.** До 2026-05-21 я отключил BE на CONS/TREND (`be_activation_pct=20` ≈ unreachable). Артём вернул BE с разными значениями на разных стратегиях — теперь это **3 параллельных эксперимента** на одних и тех же сигналах через одну и ту же лесенку TP1=2R / 100% close.

**ВАЖНО — две эпохи настроек:**

| Период | CONS act/off | TREND act/off | AGGR act/off | Заметка |
|---|---|---|---|---|
| **до 2026-05-21 19:00 UTC** (включая 30-day stats окно) | **0.5 / 0.15** | **0.8 / 0.5** | **1.5 / 0.5** | старая конфига — данные за прошлые 30 дней собирались с этими параметрами |
| **с 2026-05-21 19:00 UTC** (новый A/B/C эксперимент) | **1.6 / 0.6** | **1.8 / 0.8** | **1.5 / 0.5** | Артём руками выставил через dashboard |

JSON-источник: `config/trading_v3_artem.json` → `strategy_parameters.{conservative,trend,aggressive}.be_activation_pct / be_price_offset_pct`.

⚠ **Critical caveat для recommend engine:** любые рекомендации dashboard'а (`/api/v2/be-recommend`) на данных «до 2026-06-21» построены преимущественно на СТАРЫХ настройках, не на новых. Не применять Apply BE до того, как накопится ≥30 дней под новыми (или хотя бы 50 closed trades per strategy с `entry_time >= 2026-05-21 19:00 UTC`).

JSON-источник: `config/trading_v3_artem.json` → `strategy_parameters.{conservative,trend,aggressive}.be_activation_pct / be_price_offset_pct`.

**Почему это эксперимент.** Сигналы у CONS/TREND/AGGR — параллельные (на каждый рыночный сигнал открываются все 3 strategy-trade'а в paper-book). Поэтому **разная BE-конфигурация × одинаковый сигнальный поток** = можно сравнить напрямую. Победителем считаем тот, у которого:
- Net PnL (за 30 дней, ≥50 closed) самый высокий, AND
- Profit Factor > 1 (если хотя бы один из 3 туда выйдет), AND
- BE close % низкий + TP1 close % высокий (т.е. BE не сжирает виннеры).

**Дополнительно через [[project-tp-shadow-ladder]]:** Shadow row на каждый сигнал **открывается БЕЗ BE** (`be_level={}` в `_open_shadow_for_main`). Это даёт **4-й контрольный вариант** = «вообще без BE». Сравнение четвёрки → лучший вариант.

**Why:**
- Артём не уверен какая BE-конфигурация оптимальна и не хочет угадывать. Хочет данные.
- Унификация после эксперимента сократит mental load (одна BE-конфига вместо трёх).

**How to apply:**
- НЕ менять BE-настройки до конца эксперимента (минимум 30 дней или 50 closed trades per strategy).
- Раз в неделю (или по запросу Артёма) — формировать compare-report: per-strategy WR/PF/net/close_reason mix + shadow «no-BE» вариант для каждой strategy-семьи.
- Когда победитель ясен — POST в `/api/settings/be_activation_*` + `be_offset_*` для остальных двух стратегий + удалить остальные эксперименты из памяти.
- Compare-report можно встроить в `auto_tp_tuner.py` (новый блок «BE A/B-C/D report»). Активация — после shadow ladder data ≥30 дней (см. [[project-tp-shadow-ladder]]).

**Целевые метрики для победителя:**
- WR ≥ 33% (break-even при TP=2R)
- Profit Factor ≥ 1.2 (не на грани)
- BE close share ≤ 25% (BE редко срабатывает = TP1 чаще доедает)
- Net positive over 30d window

**Текущий timing:** Старт 2026-05-21 ~19:00 UTC. Минимум до 2026-06-21 не трогать.

**Хроника:**
- 2026-05-21 19:00 UTC — Артём выставил новые BE: CONS 1.6/0.6, TREND 1.8/0.8, AGGR 1.5/0.5. До этого момента 30 дней крутилось CONS 0.5/0.15, TREND 0.8/0.5, AGGR 1.5/0.5 (только AGGR не изменилась).
- 2026-05-21 19:00 UTC — также активирован shadow ladder (no-BE контроль) — paper-only.

**Что НЕ путать в анализе:**
- Если recommend engine говорит «BE close 39.7% → lower activation», эта статистика собрана при CONS 0.5%, а не 1.6%. Цифра «39.7% BE-close при 0.5% activation» означает что BE срабатывает почти на каждой сделке (логично — 0.5% это очень рано). При 1.6% activation ожидаемая частота BE-close будет ниже.
- Реальный сигнал об эффективности новой 1.6/0.6-конфиги увидим только когда `entry_time >= 2026-05-21 19:00 UTC` накопит ≥50 сделок на стратегию.
