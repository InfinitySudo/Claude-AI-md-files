---
name: project-btc-regime-gate
description: "BTC-led market-regime фильтр (2026-05-29): пока BTC ниже 4H EMA200 — контртренд-LONG по всем символам/стратегиям блокируется (reject BTC_REGIME_LONG_BLOCK), шорты идут. Дополняет per-symbol EMA-gate. Toggle btc_regime_enabled в Settings, дефолт ON."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9924a9cb-baa9-4aa6-aeee-d2beb8128b55
---

**Что и зачем.** Добавлен 2026-05-29 (commit `285f4da`). Глобальный market-regime фильтр поверх существующего per-symbol [[project-session-2026-05-21-tp-redesign]] EMA-gate. Анализ AGGR real показал: 148 контртренд-LONG дали net **−$32** (PF 0.58), шорты +$37 (PF 1.30) — лонги топили итог до +$4.70. Причина: per-symbol EMA-gate пропускает альт, который выше СВОЕЙ EMA на локальном отскоке, хотя BTC/рынок в даунтренде (альты ходят за BTC).

**Логика (soft mode).** В `main_bot_v3.py:_btc_regime_blocks_long()`, вызывается в `process_signal` после blacklist-чека (до position-cap). Применяется ко **ВСЕМ стратегиям, paper+real**:
- BTC текущая цена < BTC EMA(period) на TF → `direction==LONG` отклоняется, reject_code `BTC_REGIME_LONG_BLOCK` (виден в дашборд-чипах + Charts skip-таблице).
- SHORT никогда не блокируется этим фильтром.
- BTC выше EMA → лонги проходят.
- BTC EMA берётся через `bybit_api.get_klines('BTCUSDT', interval=tf, limit=period+50)`, кэш 15 мин (`self._btc_ema_cache`), fail-open при любой ошибке/нехватке данных.

**Настройки (bot_settings, hot-reload, toggle в Settings → категория signal):**
- `btc_regime_enabled` (bool, **дефолт true/ON**)
- `btc_regime_tf` (enum, дефолт `240` = 4H)
- `btc_regime_period` (int, дефолт `200`)
Читаются в боте через `_read_bool_setting/_read_int_setting`. Откат: выставить `btc_regime_enabled=false` через dashboard (без рестарта).

**Состояние на момент включения:** BTC 73158 < 4H EMA200 77484 → даунтренд, лонги блокируются по всему рынку.

**Тесты:** `tests/test_btc_regime.py` (7), full suite 246 pass.

**Отличие от EMA-gate:** EMA-gate = per-symbol (цена монеты vs её EMA, в signalbot, backend signal_json). BTC-regime = один глобальный BTC-тренд (в trading bot, backend bot_settings). Работают вместе — сигнал проходит, только если оба согласны.

См. [[project-trading-critical-params]], [[feedback-trading-analysis-protocol]].
