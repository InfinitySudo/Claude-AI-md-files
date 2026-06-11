---
name: feedback_gerchik_turnover_partial_day
description: "Gerchik throughput-киллер — turnover_usd считал оборот по неполному текущему D-бару (занижение 3-4×), фикс = среднее полных дней"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9267277e-3df1-4ed4-9b88-ec9b23834f86
---

В Gerchik-агенте (PumpDumpAI_Agent) `selection.turnover_usd` считал суточный оборот по ТЕКУЩЕМУ (неполному) дневному бару → занижал ликвидность в 3-4× → ликвидные монеты (BNB/LINK/ADA/DOGE) ошибочно не проходили `is_tradeable` ($50M-гейт) и вообще не оценивались стратегиями. Это был главный throughput-киллер (торговал почти только ЛП), а НЕ селективность метода.

**Why:** последний D-бар на бирже = текущий незавершённый день; его close×volume — частичный.

**How to apply:** оборот = среднее `close×volume` по N ПОЛНЫМ дням (default 7, отбрасываем `bars[-1]`). Сверено с Bybit tickers `turnover24h`. Эффект: tradeable 6→25 монет. Порог $50M (из курса) НЕ трогать — чинить только измерение. Commit на main (PR #3). Вселенная сканера расширена 20→33 (`config/gerchik.json`), живой is_tradeable-скрин каждый цикл выбирает активных.

⚠ Отбой/пробой давали 0 сетапов по РЕЖИМУ рынка (ложные пробои на at-level монетах), НЕ из-за бага — не форсить их триггеры ([[feedback_one_tweak_at_a_time]]). Связано: [[project_gerchik_strategy_extraction]], [[project_gerchik_proboi_subtypes]].
