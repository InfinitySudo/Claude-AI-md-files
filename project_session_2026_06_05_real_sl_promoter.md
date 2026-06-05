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

**🐞 Баг промоутера (НЕ исправлен, только отключён):** `src/trader_promotion.py` промоутит по **paper**-статистике (C paper: WR55%/PF1.3/+$30 → promote), а демоутит по **real**-истории (C real 786 строк, net −$86 → demote). Разные пулы → вечный флап. 2026-06-05 за 20 мин: 12:41 DEMOTE → 12:43 PROMOTE → 13:00 DEMOTE. Именно он поднял C в real ночью (Артём думал — сам, нет). Чинить: promote/demote должны мерить ОДИН пул (paper для кандидата, real для уже-real демоута — но не путать историю до промоушена).

**🐞 Коллизия двух real подтверждена эмпирически:** 13:00 C(real)+F(real) оба ушли в REAL ROUTE на ONDOUSDT → Bybit One-Way агрегирует → у F `SL setup FAILED`. Глобальный dup-guard (`_count_dup_positions`, REAL = по (symbol,mode) без учёта стратегии) НЕ ловит внутри одного fan-out (устаревший snapshot open_positions). См. [[project-real-global-guard-limitation]].

**Решение Артёма по dual-real:** пока только F в real, C — paper. Развести C и F по РАЗНЫМ суб-аккаунтам (чтобы оба открывали независимо без One-Way конфликта) — отдельной задачей; свободного фондированного суба нет (sub1=tradingbot, sub2=Gerchik copy, sub3=AI-agent), нужен новый + ключ + пополнение от Артёма. Код потребует per-trader executor routing (сейчас один `real_executor` на `BYBIT_API_KEY`, `main_bot_v3.py:127-138`).

**✅ SL Qty-invalid фикс задеплоен** (commit `2bf454c`, 295 pytest passed) — см. [[feedback-real-sl-qty-step]].

**Не-блокеры на потом:** (1) баг промоутера выше; (2) `daily report → telegram`: `'NotificationManager' object has no attribute 'send_message'` (отчёт не уходит).

Связано: [[project-trader-model-10]], [[project-trading-critical-params]], [[feedback-pause-button-doesnt-stop-real]].
