---
name: Trading Guards REAL only
description: Все risk-гарды в process_signal (main_bot_v3) применяются ТОЛЬКО к REAL-routed стратегиям; PAPER идёт без блоков
type: feedback
originSessionId: 82739812-5e67-4bf7-9d65-cae1428ebf23
---
С 2026-05-04 каждый risk/loss гард в `process_signal` (main_bot_v3.py) короткозамыкается для PAPER-mode сигналов:
- `_check_daily_drawdown_guard` — return (False, "") если effective_mode != REAL
- `is_symbol_blacklisted` (5+ SL streak → 48h) — обёрнуто в `if sig_effective_mode == 'REAL'`
- `_check_cumulative_drawdown_guards` (weekly+total) — уже было REAL only
- `real_blocked_hours_utc` (time-of-day) — уже было REAL only

Что осталось активным для PAPER (НЕ убирать без явной просьбы):
- Dup-position по (symbol, mode) — иначе по одной монете пачка позиций
- Debounce 60с по символу (runner) и cooldown 4-bar (signalbot) — защита от дубль-сигнала
- ATR not calculated → skip (техническое, не блок)

**Why:** Артём 2026-05-04 «нужно убрать ВСЕ ограничения для conservative торговли, она торгует без реальных денег». Логика: paper не теряет $$$, задача paper — собирать максимум данных для GA/анализа, в т.ч. по «токсичным» монетам. Гарды защищают capital — capital нет → защищать нечего.

**How to apply:**
- При hybrid-mode (CONS=paper, TREND/AGGR=real) все гарды рубят только REAL-стратегии. Если CONS снова станет real → гарды автоматически вернутся (логика mode-aware через `tm.per_strategy`).
- Если в логах видишь "🛑 BLOCKED" или "❌ REJECTED ... on auto-blacklist" — это всегда REAL.
- Не добавляй обратно блоки для paper без явной просьбы Артёма.
- Когда добавляешь НОВЫЙ гард в process_signal — оборачивай в `if sig_effective_mode == 'REAL'` по умолчанию.
