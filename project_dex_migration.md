---
name: Trading bot DEX migration (Hyperliquid)
description: Artem boitsya CEX-custody risk, sprashivayet pro Hyperliquid. Obsuzhdali 2026-04-23 strategiyu security + tech skоp porта.
type: project
originSessionId: a50e8fb7-4ba7-4e12-826b-ccf591fe559e
---
**Context:** Артём боится держать большие депозиты на Bybit (CEX, FTX-risk). Спросил про подключение нашего бота к DEX — Hyperliquid / dYdX v4.

**Технический ландшафт (2026-04-23):**
- **Hyperliquid** — L1 perp DEX, on-chain orderbook, fast finality, fees 0.025%/0.01%. Official `hyperliquid-python-sdk`. Лучший кандидат.
- **dYdX v4** — Cosmos L1, ZK proofs. Тоже хороший.
- **Aevo, Paradex** — EVM L2 perpetuals, меньше liquidity.
- **GMX, GNS** — AMM perpetuals. НЕ подходят для scalping (slippage).

**Risks specific to our bot:**
1. Slippage: из 426 символов пул Hyperliquid покрывает только ликвидные top-30. Spread 5-15 bps vs 1-3 bps Bybit. Может сломать CONSERVATIVE TP3 math.
2. No server-side TP/SL на DEX'ах — TP/SL в conditional orders работают только пока бот online. Bot down = позиция без защиты.
3. Hot wallet на VPS = single point of failure. На Bybit API-ключ с IP whitelist + disabled withdraw уже даёт comparable security.
4. Port scope: `bybit_api.py` + `order_executor_v3.py` + SL/TP mechanics — 2-4 недели работы на новый executor + reconciler + WebSocket adapter.

**Рекомендованный подход (предложил 2026-04-23):**

Настоящая защита капитала — **не exchange**, а **где лежит когда не торгуется**:
- 90%+ в hardware wallet (Ledger/Trezor) USDC/BTC, offline
- Working capital $3-5k на CEX где бот работает
- Еженедельный вывод profit в cold storage (автоматом через API withdraw whitelist)

**Если всё равно хотим DEX:** параллельный Hyperliquid-executor для AGGRESSIVE стратегии (сейчас real-mode, 0 трейдов — идеальный sandbox). Сравнить edge на реальных сделках. Если Hyperliquid показывает близкий WR при меньших fees → мигрируем CONS/TREND. Если slippage съедает edge → остаёмся на Bybit + cold storage.

**How to apply:** Если Артём говорит «делаем Hyperliquid» — открыть новую сессию, оценить scope через Plan agent. Если спрашивает «безопаснее на DEX?» — объяснить что 90% капитала должно быть в cold storage независимо от CEX vs DEX.

**Pending:** Артём не решил пока port делать или нет, ответил на обзор. При следующем возвращении к теме — узнать решение.
