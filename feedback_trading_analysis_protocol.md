---
name: feedback-trading-analysis-protocol
description: Перед любым trading-анализом (RR/break-even/SL/PnL/fees/blacklist) ОБЯЗАН прочитать project_trading_critical_params.md и текущие bot_settings — не гадать настройки из головы.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9b7a1d0f-7f87-48b6-aa9e-1e9273fc341f
---

# Правило: trading analysis — only from authoritative state

**Правило**: для каждого вопроса про break-even, RR, SL distance, fees, leverage, blacklist, hours, risk-каpы — **перед расчётом** прочитать:

1. [[project-trading-critical-params]] — текущие настройки (mode, risk, SL формула, TP, BE, fees, hours, caps)
2. При необходимости — query `bot_settings` в Postgres `trading_v3` для свежих overrides
3. При необходимости — `config/trading_v3_artem.json` (через `env_config.expand_env_vars`)

После расчёта — **обновить** `project_trading_critical_params.md` если:
- изменились bot_settings (atr_multiplier, tp_*, be_*, dd caps, leverage)
- изменился `trading_mode.per_strategy`
- появились новые R-метрики из real_trades (баки SL/BE/TP avg_R меняются по мере данных)
- Артём поменял risk_*_usd / TP-ratios через dashboard или вручную

**Why**: 2026-05-26 при разговоре про RR break-even приплёл "0.8× ATR vs 1.0× ATR" — это была чистая выдумка. Реальная формула: `ATR_15d_filtered × atr_multiplier (bot_settings, сейчас 0.25)`. Артём поймал, попросил завести memory чтобы это не повторялось. Аналогично — сказал "fee = 50% of 1R", оказалось 20% per trade / 41% round-trip. Ошибки в базовых числах ломают весь дальнейший анализ.

**How to apply**:
- Если пользователь спрашивает про RR / break-even / "минимальный TP" / "сколько надо чтобы покрыть fees" / "какой leverage" / "почему теряем" — **первым делом** Read [[project-trading-critical-params]].
- Если пользователь упоминает изменение настройки (новый atr_multiplier, новый TP, новая blacklist) — **сразу после применения** Edit [[project-trading-critical-params]] (раздел + "Last verified" дата).
- В ответах указывать source: "по `bot_settings.atr_multiplier=0.25` на 2026-05-26", не "обычно 0.25".
- Не путать legacy fields в JSON (например `order_execution.leverage=5` или `strategy_parameters.aggressive.sl_multiplier=0.1`) с реально используемыми из `bot_settings`.

См. также [[feedback-trading-config-live-source]] (Артём правит настройки через dashboard).
