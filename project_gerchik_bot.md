---
name: gerchik-trading-agent — AI agent для Bybit на price-action Герчика
description: Самообучающийся agent (rule engine + ML scorer + LLM reflector + GA evolution); /root/gerchik-trading-agent; private GitHub repo InfinitySudo/gerchik-trading-agent; шарит Bybit ключ+Postgres с 4BotsBybit-Trading
type: project
originSessionId: 93067773-cafa-4ab3-b8c6-cf84bdc85eda
---
Создан 2026-05-10 после волны фиксов Volume Spike бота. Артём решил параллельно начать AI-агента по принципам Александра Герчика — price-action на уровнях, не momentum/spike.

Изначально был назван `gerchik-bot`, переименован в `gerchik-trading-agent` потому что Артём попросил **AI agent** (не статичного бота): self-learning loop с journaling → ML scoring → weekly LLM reflection → GA evolution.

## Расположение

- **Локально:** `/root/gerchik-trading-agent/`
- **Repo:** `InfinitySudo/gerchik-trading-agent` (private, GitHub)
- **`.env` symlink** → `/root/4BotsBybit-Trading/.env` (один Bybit ключ)
- **DB:** общий Postgres `trading_bot_v3`, новые таблицы `gerchik_signals`, `gerchik_trades` (создавать в Phase 1 migration)

## Архитектура (см. docs/AGENT.md)

4-слойная модель: Perception → Reasoning → Action → Memory + Learning.

Reasoning имеет 3 источника решений в порядке важности:
1. **Rule engine** (детерминированный, immutable) — Gerchik rules: уровни, паттерны, RR≥3, MM.
2. **ML scorer** (XGBoost/LGBM, retrain weekly) — confidence score 0-1, scaling qty или skip.
3. **LLM reflector** (Claude Haiku, weekly cron) — анализ trade journal, **suggestions** для параметров; **не применяет автоматически**, только flags для approve.

Инварианты которые ML/LLM НЕ могут нарушить (hardcoded в `risk_manager.py`):
- risk per trade ≤ 2% wallet
- RR ≥ 3:1
- 3 убытка подряд → STOP до утра (Заповедь 9)
- daily_loss_cap, weekly_loss_cap
- Bybit min order $10

## Координация с 4BotsBybit-Trading

**Symbol pool split** (вариант 1 выбран Артёмом):
- Agent торгует BTC/ETH/SOL (стартовый MVP пул)
- Эти символы blacklist'им в `4BotsBybit-Trading/config/excluded_symbols.json`
- Один Bybit аккаунт, ноль конфликтов по позициям

(Sub-account отвергнут — выбран один main.)

## Phase plan

| Phase | Содержание | Status |
|---|---|---|
| 0. Spec | gerchik_rules.md, AGENT.md, ответы Q1-Q8 | **draft, ждёт ответов Артёма** |
| 1. MVP rule engine | level detector + pattern detector + paper executor + journal | not started |
| 2. ML scorer | meta-labeler shadow mode, retrain weekly | after 50+ paper trades |
| 3. LLM reflector | weekly Claude review → param suggestions с approval | after 100+ trades |
| 4. GA evolution | adaptive params на post-baseline данных | after 200+ trades |
| 5. REAL routing | переключение в real после доказанного edge | по решению Артёма |

## Текущее состояние (2026-05-10)

**Phase 1.5 — REAL trading включён для BTCUSDT (24h shake-out).**

- Repo: https://github.com/InfinitySudo/gerchik-trading-agent (private)
- Q1-Q8 resolved. Spec v0.2 финализирован.
- Symbol blacklist в Volume Spike: BTC/ETH/SOL/BNB/XRP на 48h (продлевать когда истечёт через `POST /api/blacklist/{sym}` на dashboard:8000)
- DB tables: `gerchik_signals`, `gerchik_trades`, `gerchik_state` (миграция применена)
- 28/28 pytest зелёные
- systemd service `gerchik-agent.service` enabled + active
- **Phase 2 / REAL ON ALL 5 PAIRS** (2026-05-10): BTC/ETH/SOL/BNB/XRP в REAL, risk $1/сделку
- `real_leverage=88` default, `real_leverage_overrides={"BNBUSDT":50}` (Bybit max BNB = 50x)
- Bybit max leverage verified: BTC/ETH/SOL/XRP=100x, BNB=50x
- Live state на запуске: BTC=1 уровень, ETH=2, SOL=0, BNB=0, XRP=2 (рынок-driven, ждём setup)
- Eval interval: 60s

## Поведенческие правила

- Сервис `gerchik-agent` живёт сам, можно рестартовать через `systemctl restart gerchik-agent`
- Логи: `journalctl -u gerchik-agent -f`
- При работе с этим проектом — НЕ трогать `4BotsBybit-Trading` (разные процессы)
- Symbol blacklist в Volume Spike нужно продлять каждые 48h (через `POST /api/blacklist/{sym}` на dashboard:8000)
- Тесты обязательны перед commit: `cd /root/gerchik-trading-agent && python3 -m pytest`

## Что переиспользуем из 4BotsBybit-Trading

- `bybit_api.py` — vendor-копия (не import — отдельный venv)
- `.env` через symlink (тот же Bybit ключ)
- Postgres connection params из env_config

## Что НЕ переиспользуем

- `signal_bot_v3_websocket.py` (volume spike) — другая природа
- ATR-based TP ladder
- Strategy switcher CONS/TREND/AGGR — у Gerchik одна стратегия

## Источники spec (открытые)

См. `docs/gerchik_rules.md` секцию 12. ВСЕ источники открытые публикации gerchik.com / gerchik.co + книга "Курс активного трейдера" (litres). **LMS-credentials Артёма не использовались** — ToS-нарушение.

## How to apply

- Любая работа над agent ведётся в `/root/gerchik-trading-agent/`, **не** трогает `4BotsBybit-Trading`.
- Symbol blacklist при добавлении пары к Gerchik MVP — синхронно добавлять в основной бот excluded_symbols.json.
- Tests + commits отдельные, в свой repo.
- Пока Phase 0 не финализирован (Q1-Q8) — код не пишем.
- При работе над Gerchik agent — НЕ предлагать LLM-driven trading (Claude as trader); архитектура — deterministic rule engine + adaptive overlay; LLM only as reviewer.
