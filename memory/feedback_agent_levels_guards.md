---
name: agent-levels-guards-chain
description: Полная цепочка фильтров в gerchik-trading-agent place_level() — 9 guards в порядке исполнения + DB колонки + что сохраняется
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fdfe8ecb-6a09-4f66-8869-b95289919a5d
---

`agent_levels.place_level()` (sub3 = AI agent) пропускает level через 9 фильтров в строгом порядке. Сначала дешёвые (DB), потом сетевые (Bybit/Claude). Любой return None = skip.

**Why:** Артём 2026-05-19 нашёл серию проблем подряд — flip-flop one-way mode, hour-bucket loophole, counter-trend Long в downtrend, averaging-into-loss, opposite-уровень на пути к TP, дубли (BTC Buy @ 610.33 x2, SOL Buy @ 83.12 x2), RR<3, funding/BTC игнорировались. Все фиксы в одном модуле, защита наслаивается.

**How to apply:** при любом изменении `place_level`, сохраняй порядок и не убирай гарды — каждый закрывает реальный кейс из логов.

## Порядок guards (place_level):

1. **Max 3 AI-levels per symbol** — старый защитный (margin lock cap).
2. **Opposite-side gap guard** — `min_gap = RR_MIN × SL_ATR_MULT × ATR = 1.4×ATR`. Не ставить если есть active противоположный уровень ближе чем gap → ловит flip-flop в one-way mode (BNB 639.3 ↔ 639.4 case).
3. **Position-aware path-to-TP guard** — `bybit.get_position()`, блокирует opposite-side уровень между entry и takeProfit открытой позы (reduceOnly закрыл бы рано).
4. **Same-side averaging-into-loss guard** — same-side уровень между SL и entry усреднил бы убыточную позу, не двигая SL (Gerchik: never average a loser).
5. **HTF trend guard** — `check_multi_tf_alignment(strict=False)` через EMA(50) на 4H+D. Counter-trend = оба TF против.
6. **Funding rate guard** — `risk_manager.check_funding_rate(threshold=0.05%/8h)`. Long при extreme positive funding — skip.
7. **BTC correlation guard** — для альтов: BTCUSDT 4H+D EMA(50), кэш 5 мин. Оба TF против direction → skip. BTC себя не проверяет.
8. **Content-based dedup** — `WHERE symbol AND side AND ROUND(price::numeric, 8) AND status IN (pending,placed)`. Закрывает hour-bucket дыру в order_link_id.
9. **Dynamic RR ≥ 3** — `_compute_sl_tp` ищет ближайший opposite уровень из `all_levels`, TP = level − 0.1×ATR buffer. Если `RR < RR_MIN=3` → skip. Fallback на entry ± 3×SL_dist.

## DB колонки (agent_levels) сохраняемые на INSERT:

`setup_grade`, `htf_bias_4h/d`, `sl_price`, `tp_price`, `rr_ratio`, `funding_rate`, `btc_bias_4h/d`, `volume_ratio`, `poc_price`. Используются для ML (`meta_labeler`) и для TG-карточки.

## TG `send_level_notification` блок «логика»:

```
📊 RR 1:N · TP · SL
🟩 Grade (strong/medium/weak) · est. WR %
📈 HTF: 4H · D
```

`_estimate_wr` — эвристический prior (base от grade + бонус за HTF align + штраф RR>1:5). Не back-tested, обновим когда наберём 100+ closed trades.

## Reasoning prompt (Claude Haiku) теперь получает:

`volume_ratio` (last D bar / avg(20)), `poc_price` (mid-price max-volume D bar за 30 дней), `htf_4h/d`, `btc_4h/d`, `funding_rate`.

## Связанные:
- [[project_gerchik_auto_flipper]] — отдельный модуль для триггеров вне обычного place flow.
- [[project_bybit_3sub_architecture]] — sub3 = AI-agent аккаунт.
- [[feedback_bybit_env_symlink]] — env-config гомогенный через `/root/4BotsBybit-Trading/.env`.
