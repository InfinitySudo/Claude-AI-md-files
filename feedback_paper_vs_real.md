---
name: Paper vs real trading mode
description: System is currently in PAPER mode — do not overhedge safety when restarting trading processes
type: feedback
originSessionId: 3c5941a8-e584-46d0-a8e0-72ab5293d0b2
---
The trading system is currently in PAPER mode — `trading_mode.mode = 'PAPER'` in `config/trading_v3_artem.json`. All orders go through `OrderExecutorWrapper` which routes them to `PaperTradingSimulator` and writes to the `simulated_trades` DB table. **No real orders hit Bybit.**

**Exchange state as of 2026-04-11 16:25Z:** real Bybit wallet `totalEquity=$17.38`, `real_trades` table empty, **0 open positions on the exchange** (verified via signed `/v5/position/list`). The "5 manually-placed REAL positions" noted on 2026-04-10 have been closed/removed. Dashboard's "Real Trading (ByBit)" section shows honest zeros.

**Why:** On 2026-04-10 I proposed a "cautious deployment" that stopped `bybit-tradingbot` during the publicTrade B/S fix observation, worried about real money losses from newly-firing signals. Artem corrected me: "мы же всё равно пока на paper trading режиме, потерять деньги тут невозможно". He was right — I had built a mental model around the $11.16 balance figure without checking `trading_mode`. Small paranoias waste his time.

**How to apply:**
- When touching the live trading path, first check `trading_mode` in `trading_v3_artem.json` before pricing in real-money risk.
- In PAPER mode, restarting `bybit-tradingbot` is safe — do it without extra ceremony. Same for signalbot.
- If mode ever flips to `REAL`, go back to cautious mode: stop tradingbot before deployments, verify signal quality in logs before re-enabling, etc.
- Artem may plan to flip to REAL eventually ("REAL MAINNET TRADING - $10 LIVE USDT" is in the config description). When that happens, this memory should be updated to reflect the new risk posture.
