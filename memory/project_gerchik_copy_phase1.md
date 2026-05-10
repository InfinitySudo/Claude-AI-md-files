---
name: Gerchik Copy Phase 1
description: Copy-trading pipeline для GTE Pro TG signals — Phase 1 architecture, capital, decisions, file map
type: project
originSessionId: 228deeee-d373-40e8-aded-8ba7e3a5bc9b
---
# Gerchik Copy Phase 1 — План и решения 2026-05-10

**Цель:** валидировать edge сигналов А.М.Герчика из приватного TG канала GTE Pro против нашего AI агента (Stream C). После 50 сделок решаем нужен ли Stream B (rule-based vs ML feature).

**Why:** Артём подписан на GTE Pro Pro канал. Хочет сравнить chart-ready Gerchik signals vs наш volume-momentum approach. До этого момента edge нашего агента не валидировался против external benchmark.

**How to apply:** Phase 1 — только Stream A (copy) + Stream C (existing). Phase 2 (≥50 trades) → решение по Stream B. НЕ строить B заранее — это шум, нет данных.

## Архитектурные решения (locked 2026-05-10)

| Параметр | Решение | Почему |
|---|---|---|
| Изоляция | **Bybit sub-account `gerchik_copy`** | Не Hedge Mode (риск сломать продакшн C); sub-account даёт полную изоляцию; отдельный API key |
| Капитал A | **$30-50 real** на sub-account | Real с первого дня для честного slippage; не paper |
| Entry | **Limit на ретесте уровня ±0.1%** | Ближе к стилю Герчика; если ретеста нет — пропускаем |
| Risk | **Фиксированный R:R от уровня** | SL = уровень±0.5%, TP = 2R; стандартизированно для сравнения |
| Конфликт A vs C | **Независимо** | Sub-account даёт это автоматически (разные accounts = разные книги позиций) |
| Vision API | **Claude Vision** для предзаполнения | Артём подтверждает inline-keyboard; ANTHROPIC_API_KEY нужен в .env |

## Где живёт код

`/root/gerchik-trading-agent/` (приватный GH InfinitySudo/gerchik-trading-agent)

- `migrations/002_copy_trader.sql` — новые таблицы `gerchik_copy_signals` + `gerchik_copy_trades` (отдельно от existing 001 schema чтобы не мешать level-detector)
- `src/signals_bot.py` — TG @gerchik_signals_bot (forward → Vision → confirm → DB)
- `src/copy_executor.py` — daemon listening to active signals, places limit-on-retest
- `src/subaccount_client.py` — Bybit REST на sub-account credentials
- `systemd/gerchik-signals-bot.service`
- `systemd/gerchik-copy-executor.service`
- `.env` — symlink на `/root/4BotsBybit-Trading/.env` (shared)
  - Новые keys: `BYBIT_GERCHIK_API_KEY`, `BYBIT_GERCHIK_API_SECRET`, `ANTHROPIC_API_KEY`, `TELEGRAM_GERCHIK_BOT_TOKEN`

## Dashboard integration (4BotsBybit)

- `/root/4BotsBybit-Trading/src/dashboard_api_v3.py` — расширить `/api/v2/strategy/{name}` для GERCHIK_COPY (читать из `gerchik_copy_trades`)
- `/root/4BotsBybit-Trading/TRADING_DASHBOARD.html` — новая вкладка **Comparison**: equity curves A vs C, side-by-side metrics, symbol overlap, Phase 2 progress bar
- Baseline: `entry_time >= stats_baseline_at` (per pre-baseline-v3 правило)

## Phase 2 trigger

Cron 1x/день (Calgary local). При `count(gerchik_copy_trades WHERE status='closed') >= 50` → ControlBot TG report:
- WR/Sharpe/maxDD A vs C
- Symbol overlap analysis (Герчик прав там где C ошибся? наоборот? коррелируют?)
- Recommendation: `B1` (rule-based) / `B2` (Vision feature in meta-labeler) / `skip` (Герчик не добавляет edge)

## Не путать с

- **gerchik-agent main loop** (`src/main.py`, `signal_engine.py`) — это **autonomous level detector** на 5 парах, отдельный продукт. Использует таблицы `gerchik_signals` + `gerchik_trades` из 001 schema. **Не трогать**.
- **Copy-trade pipeline** (Phase 1) — это новые таблицы `gerchik_copy_*`, новые сервисы, изолированный sub-account. **Никаких пересечений** кроме shared DB+.env.

## VPS context

- IP для Bybit whitelist: `187.77.148.44`
- DB: `trading_bot_v3` Postgres, user `trading_bot`
- TG bot infrastructure: control_bot_simple_v3.py паттерн (callback dispatcher, не python-telegram-bot)

## Status (2026-05-10)

**IMPLEMENTATION COMPLETE — awaiting Bybit sub-account credentials**

Что готово и запущено:
- ✅ Migration 002 применена (gerchik_copy_signals, gerchik_copy_trades + state keys)
- ✅ @GTE_AI_TradingBot живой, systemd `gerchik-signals-bot.service` enabled+running
- ✅ copy_executor код готов (`src/copy_executor.py`), systemd unit установлен но НЕ запущен
- ✅ Dashboard Compare tab — `index_v2.html` 7-я вкладка ⚖️ Compare (между Charts и Control)
- ✅ Endpoint `/api/v2/gerchik/comparison` работает (status=ok)
- ✅ Phase 2 timer enabled — `gerchik-phase2-trigger.timer` запускается 09:00 Calgary daily

Pending от Артёма (блокирует запуск copy_executor):
1. Создать sub-account `gerchik_copy` через Bybit UI
2. API keys (Read+Trade, no Withdrawal, IP whitelist 187.77.148.44)
3. Перевод $30-50 USDT main → sub
4. Передать keys → дописываю в `.env` (BYBIT_GERCHIK_API_KEY/SECRET)
5. После добавления keys: `systemctl enable --now gerchik-copy-executor.service`

Git commits:
- `eac8884` migration + signals_bot
- `874803c` copy_executor daemon + bybit_client extensions
- `59c6693` Phase 2 trigger + timer
- 4BotsBybit `81cf788` Compare tab + endpoint
