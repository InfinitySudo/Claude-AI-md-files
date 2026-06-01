---
name: feedback-tradingbot-stale-settings-read
description: bybit-tradingbot читает DD-threshold из bot_settings стейлово — смена weekly_max_drawdown_pct через dashboard не применяется до рестарта сервиса
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 46f870fa-7970-491c-8823-c7cddf59890d
---

2026-06-01: AGGR (real) не торговал — `DD_GUARD_CUMULATIVE` блокировал каждый сигнал «Weekly DD 28.95% ≥ **25.0%**». В DB `weekly_max_drawdown_pct` уже был поднят до 40.0 (updated_at 06:05 UTC), `/api/dd/status` (dashboard, свежий коннект) показывал threshold 40 и tripped=false — **а running tradingbot 7 часов продолжал читать 25.0** и блокировать. Свежий процесс/коннект читает правильно, бот — нет.

**Why:** `main_bot_v3._read_setting_pct` делает SELECT на долгоживущем `db_conn_ipc` без commit между циклами → коннект держит стейловый снапшот (idle-in-transaction), новые значения bot_settings не видны. PnL-цифры в том же guard слегка дрейфовали, но threshold залип.

**How to apply:** после смены любого `*_max_drawdown_pct` / guard-настройки через dashboard POST — **рестартить `bybit-tradingbot`**, иначе бот игнорит новое значение. Проверять реальное поведение по `journalctl -u bybit-tradingbot | grep "Weekly DD"`, а НЕ только по `/api/dd/status` (они читают из разных коннектов). Кандидат на фикс кода: commit/rollback перед каждым settings-read или autocommit на db_conn_ipc. Связано с [[feedback-dashboard-view-lock]] (тот же idle-in-tx класс) и [[project-trading-critical-params]] §8.
