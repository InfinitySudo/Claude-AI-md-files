---
name: feedback_pumpdump_real_qty_reconcile_dust
description: "PumpDump REAL — close-PnL в журнале берётся из ВНУТРЕННЕЙ модели TP/BE, а не из реального closedPnl Bybit → расхождение; +dust после TP3"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3814021d-32b9-44d3-87ae-8a21ce804338
---

2026-06-13/14: на панели Trading Panel+AI Tools (pumpdump, sub-4, REAL) TAOUSDT показал Net PnL
**+$5.45**, а реально на бирже **+11.4948 USDT**. Сверка через Bybit `/v5/position/closed-pnl`:
4 закрытия (qty 1.09+1.818+0.727+0.001 ≈ 3.636 TAO), реальные exit'ы 272.4–274.25, **Σ closedPnl
= +11.4948** (ровно как в скрине Артёма). qty 3.636 в журнале был ВЕРНЫЙ; «0.001 TAO» из скрина = это
DUST-остаток (4-я запись, +0.003).

**Корень PnL (исправленная диагностика):** журнальная запись close посчитана из ВНУТРЕННЕЙ модели
трекера (tp1@270.59 + tp2@271.35 + BE@270.08 → net 5.448), а не из реальных филлов биржи (272–274).
Трекер занизил. Это НЕ про плановый qty (qty был верный). Настоящий фикс на будущее: на закрытии
тянуть `closedPnl` из Bybit и писать ЕГО в журнал, не доверять модельным TP/BE-ценам. ⏳ не сделано.

**Сделано:**
- Разовая правка записи `TAOUSDT-1781403095114`: net 5.448→**11.4948**, gross→11.92, R→5.747,
  exit→272.78, exit_reason→TP3, поле `_reconciled_from_bybit`. Бэкап journal.jsonl.bak-taofix-*.
  stats_24h теперь отдаёт +11.4948 → панель показывает правду (читает журнал пер-реквест, рестарт не нужен).
- **Dust после TP3** (executor.set_sl_tp): по-кусочный floor `tp_qty=qty*dist` к qtyStep оставлял
  остаток → последний TP теперь закрывает ВЕСЬ остаток (`qty−placed`). Подтверждено: 0.001 dust-запись.
- qty-сверка с биржей в main.py (после входа real_size vs план) — безвредный сейф-нет (на TAO не сработал,
  qty совпал), полезен на реальных частичных филлах.

⚠ Креды sub-4 в `.env` (BYBIT_API_KEY=e2KPVwqD…) — но в окружении торчит `test_key_123`-ловушка
([[feedback_sl_zero_position_race]]): грузить .env с OVERRIDE (os.environ[k]=v), не setdefault, иначе 401.
`pumpdump.service` (REAL sub-4, :8004), панель :8080. ОТДЕЛЬНЫЙ от Герчика. См. [[project_pumpdump_semiauto]].

**2026-06-13 систематические правки «окно подготовки = биржа = P&L» (тикет pumpdump.html + бэкенд):**
- **Реальное плечо в тикете:** новый эндпоинт `/instrument?symbol=` (http_server → executor._instrument_spec,
  публичный, кэш) отдаёт max_leverage Bybit (TAO=50×). Тикет тянет его, клампит поле плеча к
  min(введённое, max_монеты, account_cap=80) → показывает РЕАЛЬНОЕ плечо (введёшь 88 → станет 50), маржа пересчитана.
- **TP1 3R в показе:** бэкенд форсит `tp1_min_R=3` (`_clamp_tp1`) → тикет теперь сам клампит поле TP1 к 3R-полу →
  экран = исполнению (R/PnL верные). Что в окне = то на бирже = то в P&L.
- **Орфан-ордера:** при закрытии (особ. по SL) невыполненные TP-условные висели reduce-only. `_on_trade_close`
  (REAL) → `executor.cancel_conditional_orders(sym)` (cancel-all StopOrder) снимает орфаны.
- **closedPnl-сверка:** `_on_trade_close` фоном `_reconcile_close_pnl` → `executor.closed_pnl_since(sym, ts_open)`
  (сумма chunks с биржи, 4×retry×2с) → патчит журнальную запись net/gross/r (`_pnl_source=bybit_closed_pnl`,
  сохраняет model_net_pnl_usd). ⚠ rewrite журнала — мелкая гонка с append (низкая частота, ок).
Правки в /var/www/dashboard/pumpdump.html + зеркало /root/Space_Live/public/pumpdump.html (статика, reload).
