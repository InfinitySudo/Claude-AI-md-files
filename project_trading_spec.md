---
name: Trading Bot Full Specification
description: Complete specification for 4 Bybit futures trading bots - strategies, signal logic, ATR calculation, TP/SL levels, strategy switching, and reporting
type: project
originSessionId: 49c33260-9917-48ee-b56d-6488fc6efafa
---
## Trading System Overview

Futures trading on Bybit. Risk per trade: $0.1-$1. Leverage: x35-x80.

## Two Strategies

### Conservative (RR 1:5) — calm market
- Risk per trade: **$0.1** (constant)
- SL: 10% of 5D ATR
- TP levels (partial close):
  - TP1(c) 1:1 — close 50%
  - TP2(c) 1:3 — close 30%
  - TP3(c) 1:5 — close 20%
- BE activation: price moves +2.5% in trade direction → set BE at entry +0.5%, close 100%

### Trend (RR 1:18) — strong directional market
- Risk per trade: **$1**
- SL: 10% of 5D ATR (same calculation)
- TP levels (partial close):
  - TP1(t) 1:3 — close 20%
  - TP2(t) 1:6 — close 20%
  - TP3(t) 1:10 — close 40%
  - TP4(t) 1:14 — close 10%
  - TP5(t) 1:18 — close 10%
- BE activation: price moves +3.5% in trade direction → set BE at entry +1%, close 100%

## Four Bots

### 1. SignalBot
- Receives and processes data from Bybit
- Sends signal to TradingBot when conditions met:
  - Volume >= $100K
  - Volume spike x2 vs average (average = 5 bars of 5-min candles)
  - Buy/sell volume ratio >= x2

### 2. TradingBotByBit
- Calculates ATR from 5 daily candles (fetches 10 to filter anomalies)
  - Anomaly filter: exclude bars > 1.8x ATR or < 0.5x ATR
  - ATR = (High - Low) / 5 from valid bars
- SL = 10% of average 5D ATR
- Places orders with correct TP levels based on active strategy
- Manages BE (breakeven) logic
- Must respect minimum order sizes on Bybit — filter out coins where $0.1 risk doesn't meet minimums

### 3. ControlBotByBit
- Monitors statistics, switches strategies
- Switch Conservative → Trend: when >=35% of last 10 trades closed at TP2+
- Switch Trend → Conservative: when <20% of last 10 trades closed at TP3(t)+
- Data from PostgreSQL statistics database

### 4. SmartBotByBit (Reporter)
- Aggregates and displays trade statistics
- Reports: daily, weekly, monthly, yearly
- Shows closed orders summary
- All connected via Telegram bots

## Architecture
- All 4 bots connected to Telegram
- Built and tested separately, but work together
- Shared PostgreSQL database for statistics and IPC

**Why:** User wants a fully automated trading system with dynamic strategy switching based on performance.
**How to apply:** Every implementation decision should align with this spec. Reference specific sections when building each bot.
