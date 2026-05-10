---
name: BE offset interpreted as % of entry price (NOT % of SL distance)
description: Обнаружено 2026-05-08: be_price_offset_pct=3.0 означало SL → entry+3% на LONG, фактически делало BE второй TP — реальный bug в GA-выводе/коде; правильные значения 0.1-0.5%
type: feedback
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
Rule: `be_price_offset_pct` в `trading_v3_artem.json:strategy_parameters.<strategy>` — это **процент от entry price**, не от SL distance. Реалистичные значения **0.05-0.5%** (просто покрыть fees + лочнуть tiny win). Значения >1.0% делают BE по сути вторым TP — SL прыгает выше entry на LONG, мгновенный close на любом маленьком retrace.

**Why:** GA после прогона 2026-05-07 выставил CONS be_price_offset_pct=3.0. С be_activation_pct=0.5%, при срабатывании BE на 0.5% прибыли SL двигался к entry+3% (LONG), что было ВЫШЕ текущей цены → instant fill. По сути работало как «закрыть на +3%», не как защитный BE. На 14 днях paper: 461 TP1-touched, 78.1% реверт к BE с avg +$0.76 вместо нормального BE-bounce 0.05-0.15%. Артём 2026-05-08 попросил снизить.

**How to apply:**
- При любом GA-apply / manual-edit BE values: проверять be_price_offset_pct < 1.0 для всех стратегий
- Дефолты sane: 0.1% (CONS/TREND), 0.05% (AGGR — выше leverage = меньше зазор)
- Если bot говорит «41% TP1 hit но 2% close» → проверить first BE offset, скорее всего > 1%
- В UI dashboard поставить min/max=0.05/2.0 на этот setting когда выпасет в SETTINGS_REGISTRY (сейчас правится через trading_v3_artem.json напрямую)
- **GA fitness формула не штрафует** за высокий BE offset — это известный gap, не учитывать как «GA знает лучше»
