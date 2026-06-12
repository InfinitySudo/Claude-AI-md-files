---
name: feedback_pumpdump_offline_maybe_emit
description: Панель pumpdump уходит в OFFLINE из-за CPU-спина _maybe_emit (O(N) на каждом трейде); фикс emit_throttle_ms
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 89d74798-546c-417b-896a-ac4e2c3a21e0
---

Панель pumpdump (:8004, [[project_pumpdump_semiauto]]) периодически показывала **OFFLINE** и сервис рестартился каждые ~25–55 мин.

**Корень (найден py-spy dump живого процесса, 2026-06-08):** `Detector._maybe_emit` вызывается на КАЖДОМ публичном трейде (`_on_trades`) и делает несколько O(N) сканов deque `trades_5m` (maxlen=5000) — `vol_in_window`/`imbalance_in_window`/`price_change_pct`, ×568 символов. Во время трейд-шторма (памп — ровно когда бот и нужен) это сатурирует ядро (CPU 55–64%), event-loop держит GIL в `vol_in_window` (detector.py:62), `/klines` не отвечает за 8с → watchdog `pumpdump-health.service` ловит 2 фейла и рестартит → панель OFFLINE на ~25с. «hot_movers fetch failed» в логе перед рестартом — спутник (Bybit REST тоже страдает в волатильность), не причина.

**Why:** O(N)-агрегаты пересчитывались на каждом сообщении, хотя окна минутные, cooldown часов — переоценка чаще раза в секунду бессмысленна.

**How to apply:** добавлен троттл `emit_throttle_ms` (дефолт 1000) + `_SymbolStats.last_emit_ms` — тяжёлая оценка максимум раз/сек на символ. Live-цена идёт отдельно через `on_tick`, НЕ троттлится. Результат: CPU 55%→0.1%, `/klines` 8с→18мс, MainThread idle в `select`. Качество сигналов не страдает.

⚠ Правка ЖИВАЯ но НЕ закоммичена (сервис крутится из рабочего дерева /root/PumpDumpAI_Agent). В дереве также чужая незакоммиченная правка `max_topics_per_ws 400→100` (даёт 12 WS-шардов по 50 символов) — НЕ моя, не трогал. Диагностика: `py-spy dump --pid $(systemctl show -p MainPID --value pumpdump.service) --nonblocking`.

Артём (2026-06-08) хотел смотреть свечи за весь 2026/всю историю монеты — это УЖЕ работает через ТФ D (500 дн ≈ 1.4 года) / W (≈10 лет); тяжело только год на 5м (~105к баров → лагает). Решил график не трогать, чинить краш-луп.
