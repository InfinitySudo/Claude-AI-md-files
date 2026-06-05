---
name: project_session_2026_06_05_real_sl_promoter
description: "2026-06-05: F=real единственный, C=paper, автопромоутер ВЫКЛЮЧЕН (флап-баг), SL Qty-invalid фикс; план — F на отдельный суб для dual-real"
metadata:
  node_type: memory
  type: project
  originSessionId: ce36190d-1e66-4ff8-83ca-991871de4019
---

Сессия 2026-06-05 (аудит real-торговли C+F по запросу Артёма «проверить чтобы без лагов/сбоев»).

**Текущее боевое состояние:**
- `trader_real_enabled`: только `trader_f=true` (REAL), все остальные false. **F = единственный real-трейдер** (cons-движок, clone A, risk $1, на sub1/`BYBIT_API_KEY`).
- **C = paper.** Метрики C: WR 50.8% / PF 1.18 (ниже порогов промоушена 55%/1.3). У C 7 открытых real-позиций (наследие ночного авто-real, все со стопами) — доезжают server-side, новые не открываются.
- **Автопромоутер ВЫКЛЮЧЕН** мной через `POST /api/settings/promo_enabled {value:false}` (`trader_promotion.enabled=false`).

**✅ Баг промоутера ИСПРАВЛЕН (commit `6a561dd`).** Был: `src/trader_promotion.py` промоутил по **paper** (C paper: WR55%/PF1.3/+$30 → promote), а демоутил по **всей real-истории** (C real 786 строк incl. легаси AGGR, net −$86 → demote) — свежепромоутнутый падал на чужих убытках → вечный флап (12:41 DEMOTE→12:43 PROMOTE→13:00 DEMOTE). Именно он поднял C в real ночью (не Артём вручную).
Фикс: (1) **demote судит real только с `trader_promoted_at`** (или окно, что позже) → свежий promote имеет <demote_min_trades → hold; (2) **`promote_cooldown_hours`=24** — после demote paper-кандидат не переподнимается; (3) `apply()` пишет `trader_promoted_at`/`trader_demoted_at`. +6 тестов (301 passed). Промоутер ОСТАЁТСЯ `enabled=false` — Артём включит когда захочет (теперь без флапа). tradingbot перезапущен (код загружен).

**🐞 Коллизия двух real подтверждена эмпирически:** 13:00 C(real)+F(real) оба ушли в REAL ROUTE на ONDOUSDT → Bybit One-Way агрегирует → у F `SL setup FAILED`. Глобальный dup-guard (`_count_dup_positions`, REAL = по (symbol,mode) без учёта стратегии) НЕ ловит внутри одного fan-out (устаревший snapshot open_positions). См. [[project-real-global-guard-limitation]].

**Решение Артёма по dual-real:** пока только F в real, C — paper. Развести C и F по РАЗНЫМ суб-аккаунтам (чтобы оба открывали независимо без One-Way конфликта) — отдельной задачей; свободного фондированного суба нет (sub1=tradingbot, sub2=Gerchik copy, sub3=AI-agent), нужен новый + ключ + пополнение от Артёма. Код потребует per-trader executor routing (сейчас один `real_executor` на `BYBIT_API_KEY`, `main_bot_v3.py:127-138`).

**✅ SL Qty-invalid фикс задеплоен** (commit `2bf454c`, 295 pytest passed) — см. [[feedback-real-sl-qty-step]].

**✅ Daily report исправлен (commit `8e28c19`).** Было 2 бага: (1) `daily_reporter.py` звал `self.telegram.send_message()`, а `self.telegram`=`NotificationManager` (метод `_send_telegram(text)`, не send_message) → AttributeError каждый день; (2) тело отчёта на легаси CONSERVATIVE/TREND — после миграции на 'Trader A–F' эти ключи пустые → нули. Теперь итерирует `trader_registry`, берёт real_trades/simulated_trades по `trader_real_enabled`, рендерит per-trader (trades/WR/PF/net, 💰real/📒paper). Smoke по живой БД — все 7 трейдеров корректно.

**Не-блокеров не осталось** — все три бага сессии закрыты (SL Qty-invalid, промоутер-флап, daily-report).

Связано: [[project-trader-model-10]], [[project-trading-critical-params]], [[feedback-pause-button-doesnt-stop-real]].
