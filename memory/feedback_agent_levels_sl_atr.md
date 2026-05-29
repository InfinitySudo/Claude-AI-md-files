---
name: feedback-agent-levels-sl-atr
description: История изменений SL_ATR_MULT в gerchik-trading-agent — компромисс между шириной SL (защита от wick-out) и пропускной способностью через RR_MIN=3.0 фильтр.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a7c17f24-1434-4a2c-b45d-6a43248a8f2f
---

`/root/gerchik-trading-agent/src/agent_levels.py:154` — константа `SL_ATR_MULT` определяет ширину SL как `± mult × ATR_14d` от уровня.

**История изменений:**
- 1.5 (исходно): SL = 1.5×ATR → ~5.2% на XRP — слишком широко для bounce-сетапов
- 0.7 (2026-05-18, Артём): компромисс — ~2.4% на XRP, баланс защиты от noise vs RR
- **0.2 (2026-05-27, Артём)**: агрессивно — ~0.5-0.7% от entry. Цель: пройти `RR_MIN=3.0` фильтр на гораздо больше setups (sl_dist в знаменателе RR). Trade-off: wick-out риск **резко вырос**, любой шум за уровнем = SL

**Why 0.2**: за неделю было только 1 active level (BTCUSDT) из-за того что RR с 0.7×ATR давал 1-1.5 при близких opp-уровнях. С 0.2×ATR sl_dist в 3.5× меньше → RR пропорционально выше → setups проходят гейт.

**How to apply**:
- Если в логах за 24-48h видим много новых placed/filled — оставляем 0.2
- Если placed но **большинство SL** (быстрое исполнение в минус) — wick-out гипотеза подтвердилась, **откатить к 0.5 или 0.7**
- Откат: `sed -i 's/SL_ATR_MULT = 0.2/SL_ATR_MULT = 0.5/' /root/gerchik-trading-agent/src/agent_levels.py && systemctl restart gerchik-agent`
- Изменение через **код-правку**, НЕ через bot_settings (Артём пометил «можно вынести в bot_settings позже», но пока в hardcode)

**Мониторинг**: systemd timer `gerchik-sl-check.timer` запускается через 2h после правки, шлёт отчёт в TG (Report-bot → chat 504609639) с количеством placed/skipped и причинами.

Связано: [[project-pumpdump-agent]], [[feedback-one-tweak-at-a-time]] (правки по одной + измерение).
