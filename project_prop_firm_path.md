---
name: Prop firm funding path ($50-150k)
description: Artem rassmatrivayet prop firm challenge kak path k $10k/mo. 2026-04-23 soglasovano — otlozhit do proven edge, kriterii gotovnosti zafiksirovany.
type: project
originSessionId: a50e8fb7-4ba7-4e12-826b-ccf591fe559e
---
**Context (2026-04-23):** Артём спросил — не пройти ли prop firm challenge чтобы получить $50-150k funded account для торговли через наш бот. Обсуждали, решили **отложить**.

**Landscape crypto prop firms:**
- Fintokei, Crypto Fund Trader, Hola Prime, The Funded Trader (crypto plan), FTMO Crypto
- Accounts $25k-$400k, challenge fee $300-1000, payout 80-90% профита
- $100k funded × 10% месяц × 80% payout ≈ $8k/мес — близко к $10k target

**Три блокера для нашего бота сейчас:**
1. **API не Bybit.** Prop-брокеры дают MT5/cTrader/proprietary broker. Порт `bybit_api.py` → MT5 = ~3-4 недели + spread/commissions на prop-брокере хуже retail Bybit в 2-3 раза → edge сжимается.
2. **Challenge rules не совместимы.** Max 5% daily DD, max 10% overall DD, запреты weekend/news. Нужен **risk governor модуль**: halt торговлю перед нарушением, dynamic position sizing, cutoff после N SL подряд. Сейчас его нет.
3. **Edge слабый.** `project_backtest_findings`: spike=6 +42% BTC+ETH, −13% median top-100. CONSERVATIVE 24h: WR 42%, 16 SL из 28. Для prop надо **+15-20% gross/мес stable**. Real trades: 1 open, 0 closed — данных нет вообще.

**Критерии готовности (когда возвращаться к теме):**
1. **30+ real trades** на Bybit с нашим ботом (track record)
2. **Proven edge ≥ +5% net/мес на real money** минимум **3 месяца подряд**
3. **Risk governor модуль** в боте (daily DD cutoff, overall DD cutoff, position size cap, rules-aware)
4. **MT5 / prop-broker API адаптер** написан и оттестирован

**Экономика провала сейчас:**
- 1 попытка = $500 + 3-4 недели времени, ~5-10% шанс с текущим edge
- 5 попыток = $2500 + 4-6 мес, ~25-40% что хоть одна пройдёт
- Альтернативное использование $2500: $3-5k working capital на Bybit + USDC cold storage

**How to apply:** Если Артём спросит «готовы ли к prop firm challenge?» — проверить по критериям выше:
- `SELECT COUNT(*) FROM real_trades WHERE status='closed' AND created_at > NOW() - INTERVAL '90 days';` → должно быть 30+
- `SELECT SUM(realized_pnl_usd - fees_paid_usd) / 3 AS avg_monthly_net FROM real_trades WHERE status='closed' AND created_at > NOW() - INTERVAL '90 days';` → должно быть ≥ +5% от капитала
- Если оба критерия — OK, обсуждаем конкретный firm (Fintokei для crypto → лучший сейчас). Иначе — преждевременно.

**Парал. вариант если деньги не жалко (не делаем):** $500-1000 на один FTMO Crypto 10k challenge вручную (не автоматом) как обучающий эксперимент чтобы увидеть как rules ломают стратегию в деле. Не путь к $10k/мес, а feedback loop.
