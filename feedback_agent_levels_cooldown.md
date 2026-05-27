---
name: agent-levels-cooldown
description: "AI Trading Agent (sub3) пересоздавал тот же уровень через 5-15 минут после fill/expired — 6h cooldown в place_level блокирует. existing_active guard ловит только status='placed', нужна отдельная проверка для filled/expired."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5f710c91-70ab-4a43-a321-815629354fd0
---

**Rule:** В `gerchik-trading-agent/src/agent_levels.py:place_level()` две проверки дедупликации, обе обязательны:

1. **existing_active** — `(symbol, side, price)` + `status IN ('pending','placed')` → возвращает existing id, skip. Это classic dedup для активных.
2. **recent_done** — `(symbol, side, level_type, price)` + `status IN ('filled','expired')` + `updated_at > NOW() - INTERVAL '6 hours'` → skip с `return None` (НЕ возвращает existing id — каждый filled был валидной сделкой).

**Why:** Без второй проверки после fill engine на следующем 60s-цикле снова видит ту же поддержку/сопротивление и через ~5-15 мин создаёт новый limit-order на той же цене. Конкретный кейс: BNBUSDT Buy support 651.67 — 4 copies в 24h (id 146→147→148→149, gaps 11min..5h). В cockpit feed «AI_TRADING_AGENT» показывал 5 одинаковых строк «BNB support 80%».

**How to apply:**
- Любая логика которая «возвращает существующий level» должна учитывать что filled — это валидная завершённая сделка, не aliasable как existing. Поэтому recent_done возвращает `None` (новый цикл, ничего не делаем), а не `recent_done['id']`.
- `level_type` обязательно в WHERE: support vs resistance на одной цене — разные сетапы (cross-over zone).
- `ROUND(price::numeric, 8) = ROUND(%s::numeric, 8)` — DB хранит NUMERIC(20,8), Python float может отличаться в последних знаках.
- 6h — компромисс: 5-15min gaps были типичны → меньше не поможет, целые сутки заблокировали бы legit retests volatile-зон.
- Если cooldown сработает на legitimate setup — лог `skipped — recent {status} (id=N), 6h cooldown` поможет понять причину.

Связано: [[feedback-agent-levels-tg-dedup]] (TG-нотификации dedup через tg_notified_at), [[project-bybit-3sub-architecture]] (sub3 = AI-agent).
