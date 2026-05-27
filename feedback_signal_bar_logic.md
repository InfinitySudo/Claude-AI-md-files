---
name: SignalBot бары — confirm-only + ws_config-aware slicing
description: Три скрытых бага в signal_bot_v3_websocket.py: interim бары как закрытые, hardcoded [-6:] vs ws_config['volume_avg_bars'], недостаточный REST-warmup
type: feedback
originSessionId: 93067773-cafa-4ab3-b8c6-cf84bdc85eda
---
WS Bybit `kline.5.*` шлёт обновления каждую ~1 секунду на протяжении всех 5 минут жизни бара (`confirm=False`), и **финальный апдейт с `confirm=True`** ровно один раз в момент закрытия (примерно через секунду после `:00/:05/...`). Раньше код signal_bot_v3_websocket.py ошибочно трактовал каждое промежуточное обновление как закрытый бар → `klines_5m` забивался десятками снапшотов одного и того же бара → spike_ratio≈1.0 → silent reject → 0 сигналов.

Три бага которые надо держать вместе (фикс 2026-05-09):

1. **`_on_new_kline`**: дедуп по `startTime` (replace last entry если тот же бар, иначе append) + `if not kline.get('confirm'): return` перед `_check_signal`. Старый комментарий "ByBit отправляет ТОЛЬКО закрытые свечи!" был неправильным.

2. **Hardcoded slice `[-6:]`**: caller передавал в `_check_signal` 6 баров, а `_check_signal` использует `bars_needed = self.ws_config['volume_avg_bars']` (живой config = 8). Внутри `len(closed_klines) < bars_needed` → silent `return None` (DEBUG-уровень). **Slice ДОЛЖЕН считаться от `max(volume_avg_bars, trend_bars)`**, не хардкод. Никогда не оставлять `[-N:]` с магической N в hot-path.

3. **REST warmup**: `initialize_symbol_history` подгружал только дневные. Сигналы фиксились бы только через 30-60 минут после рестарта. Теперь грузит и 5m bars (warm_count = max(volume_avg_bars, trend_bars) + 2). raw[0] = текущий открытый бар, его пропускаем.

**Why:** signals_queue стояли с 2026-05-08 17:01 24+ часа. WS reconnect/keepalive (commit `6780ec6`) починил подключение, но spike-расчёт всё равно ломался от interim-баров и mismatched slice size. Артём успел понизить пороги до spike=2.0/100k и не понимал почему — проблема была глубже фильтра.

**How to apply:** при любом изменении в SignalBot pipeline проверять:
- `_on_new_kline` фильтрует на `confirm=True` (interim обновления только апдейтят последнюю запись)
- Все срезы `klines_5m[-N:]` берут N из `ws_config['volume_avg_bars']`/`trend_bars`, **не магических констант**
- REST warmup даёт минимум `max(volume_avg_bars, trend_bars)` закрытых баров

Диагностика будущих "нет сигналов":
- `tail logs/signal_bot_runner_v3.log` — должны идти `📊 Spike calculation` и `🔍 SPIKE CALC` каждые 5 минут
- Нет `SPIKE CALC` после bar close = `_check_signal` тихо отбрасывает на первой же проверке (`len(closed_klines) < bars_needed` или `volume_usd < threshold`)
- В `dashboard_api_v3` через `/api/signals/last` или прямо `signals_queue` SQL — последний `created_at` должен быть < 1 час назад в активном рынке

Файлы: `src/signal_bot_v3_websocket.py:_on_new_kline` (≈line 269), `:initialize_symbol_history` (≈line 178), `:_check_signal` (≈line 350+).
