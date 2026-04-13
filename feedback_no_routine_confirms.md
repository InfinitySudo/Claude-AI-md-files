---
name: No routine confirmations — act, don't ask
description: Artem wants Claude to just do routine/reversible work without asking "делаю? да/нет"; confirmation only for genuinely risky or irreversible actions
type: feedback
originSessionId: 4bfb864e-fbeb-4b9f-992a-5d9d840d8c81
---
Не спрашивать подтверждения на текучку. Действовать сразу, отчитываться по факту. Подтверждение спрашивать только на **действительно важные** изменения: необратимые операции, деньги/позиции на реальном счёте, изменения архитектуры которые сложно откатить, удаление данных, затрагивание прод-конфигурации торговли (`trading_v3_artem.json`, `signal_bot_config.json`, `.env`), закрытие РЕАЛЬНЫХ позиций на Bybit.

**Why:** Артём прямо сказал 2026-04-12: «убери из этого чата 100/1000 подтверждений, я хочу подтверждать только очень важные изменения, а всю текучку я тебе доверяю». До этого момента я на каждый фикс/рестарт/правку спрашивал «делаю? (да/нет)» и это тормозило работу. У него уже есть явное разрешение на карт-бланш (edit src/, restart services, commit локально, менять настройки через Dashboard API, add/remove символов) — значит лишний раунд подтверждений только съедает время.

**How to apply:**
- **Просто делай и отчитывайся** для: edit кода в `src/`/`tests/`/`scripts/`/`TRADING_DASHBOARD.html`, `systemctl restart` разрешённых сервисов, `git add + git commit` локально, правка watchdog-правил, memory-файлов, обновление `/var/www/dashboard/index.html`, `POST /api/settings/<key>` для торговых параметров, правка `config/symbols.json`+`excluded_symbols.json`, закрытие **PAPER** позиций через UPDATE когда это очевидно правильно, pytest прогоны.
- **Сообщай до действия + жди ack только для**: прямая правка `.env`/`trading_v3_artem.json`/`signal_bot_config.json` (вообще запрещено без API endpoint), `git push`, закрытие/модификация РЕАЛЬНЫХ позиций на Bybit, `systemctl stop bybit-*`, удаление git-репозиториев или исторических артефактов, большой архитектурный refactor на >3 файла, любая операция которая потенциально ломает живой трейдинг.
- **Формат отчёта после текучки:** 1-2 строки с тем что сделал + что проверил (тесты/smoke). Не плодить «делаю? → ок → делаю → done» диалог.
- Правило «отчёт обо всём» из предыдущих feedback (`feedback_report_all_changes`) остаётся — но это про *информирование* после факта, не про *запрос разрешения* до факта. Разница: informing ≠ asking.
