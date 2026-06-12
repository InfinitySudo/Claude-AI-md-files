---
name: feedback_sl_zero_position_race
description: "SL не встаёт при гонке вход↔SL (Bybit 10001 'zero position'); set_trading_stop надо ретраить после появления size>0"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a93451ef-0f6d-41bb-a1bb-cf747ced118c
---

Инцидент 2026-06-11: реальная позиция MAGMAUSDT (short 20x, sub-аккаунт `pumpdump`,
ключи в `PumpDumpAI_Agent/.env`) осталась БЕЗ стоп-лосса. `set_trading_stop` вернул
**retCode 10001 'can not set tp/sl/ts for zero position'** — SL отправили раньше, чем биржа
зарегистрировала позицию (maker-вход / innovation-zone токен ещё не исполнился), и повтора не было.
TP-лесенка (conditional reduceOnly order/create) прошла — она НЕ требует открытой позиции, а
`set_trading_stop` требует. Итог: тейки есть, стопа нет.

**Why:** позиция с плечом без SL = недопустимый риск. Watchdog в `tracker.py` не дорабатывал
(процесс-владелец не был запущен; жил только run_gerchik).

**How to apply:**
- Фикс в `executor.py` (commit 5bf441e): `_set_sl_market_retry` — до 6 повторов с ожиданием
  `_position_open` (size>0); `force_sl`/`set_sl_tp` через него; полный провал → громкий ERROR.
- Ручная установка SL по живой позиции: `set_trading_stop(symbol, sl_price, sl_size=100,
  sl_order_type=Market, tpsl_mode=Full, sl_trigger_by=MarkPrice)` через `ByBitAPI`
  (`/root/4BotsBybit-Trading/src/bybit_api.py`).
- ⚠ ЛОВУШКА окружения: в шелле сессии торчал `BYBIT_API_KEY=test_key_123` → `os.environ.setdefault`
  его НЕ перетирал → 401/10003. При скриптах против `.env` ФОРСИТЬ `os.environ[k]=v`, не setdefault.
- ⚠ `ByBitAPI.get_open_positions` (GET) даёт 401 при кривом ключе так же как POST — проверяй ключ.
- Реальные действия с ордерами — только с явного разрешения Артёма ([[feedback_bybit_migration_bypass]]).
**ВТОРОЙ КОРЕНЬ (commit b74406d):** `executor.get_open_positions` звал НЕсуществующий `self._api.get_positions(...)` → AttributeError → `[]`. Поэтому watchdog («100% SL guarantee», backup) НИКОГДА не видел позиции — страховка была СЛЕПА (не переставила SL у MAGMA), и реконсиляция не находила сирот. Правильный метод ByBitAPI — `get_open_positions()` (готовый список raw-позиций linear/USDT).

**Усыновление сирот (commit 1106da8):** `Agent._reconcile_open_positions` (REAL) теперь после файла опрашивает биржу и усыновляет живые позиции, которых нет в локальном стейте (`_adopt_exchange_orphans` → минимальная `Position` entry=avgPrice, sl=stopLoss, tp=[], be_enabled=False). Дашборд `:8080/pumpdump.html` берёт позиции из `tracker._positions` (стейт бота, не биржа) через `/stats` → `_open_positions_detail`; поэтому невидимость = позиция не в трекере. MAGMA усыновлена, SL цел, видна.

**ТРЕТИЙ КОРЕНЬ — фантомные сделки (commit ae2e23c):** бот ставил entry (Post-Only Limit) и СРАЗУ `set_sl_tp` не дождавшись филла → 'zero position' → SL не вставал → фантомные open/close (BEATUSDT, MAGMA). Фикс `executor.open_confirmed`: Limit(maker) → `_await_fill` (поллит позицию size>0, timeout `entry_limit_timeout_sec`) → не налилось → cancel лимит + Market(гарантия) → ok=True ТОЛЬКО при реальной позиции. `main` журналит/трекает сделку лишь после подтверждённого входа; если SL не встал при открытой позиции — флэтчит (позиция без стопа недопустима). Итог: вход всегда наливается, SL/TP всегда выставляются, либо сделки нет вовсе.

Связано: [[feedback_real_sl_qty_step]], [[feedback_conditional_order_cleanup]], [[feedback_bybit_tp_limit_quirks]].
