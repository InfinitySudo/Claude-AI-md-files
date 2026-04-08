# 🎮 SYSTEM AUTONOMY TEST - Complete Control Bot Verification

**Purpose:** Verify that ALL system functions work independently via Control Bot WITHOUT Dex assistance.

**Last Updated:** 2026-04-03 23:09 UTC  
**Status:** ✅ READY FOR TESTING

---

## 📋 TEST CHECKLIST

### Phase 1: Bot Lifecycle Management (5 minutes)

**1.1 START BOTS**
```
Menu: 🟢 Start
Expected:
  ✅ Trading Bot starts (PID visible)
  ✅ Signal Bot starts (WebSocket connects)
  ✅ "ALL SYSTEMS ONLINE" alert in Telegram
  ✅ Status shows all ALIVE
Verify: ps aux | grep python3 (3 bot processes)
```

**1.2 CHECK STATUS**
```
Menu: 📊 Status
Expected:
  ✅ Signal Bot: ✅ ALIVE
  ✅ Trading Bot: ✅ ALIVE
  ✅ Strategy Switcher: ✅ ACTIVE
  ✅ Current Strategy: CONSERVATIVE
  ✅ Statistics shown (signals, trades, win rate, P&L)
```

**1.3 STOP BOTS**
```
Menu: 🛑 Stop
Expected:
  ✅ All bots stop gracefully
  ✅ No error messages
  ✅ Process verification: ps aux | grep python3 (0 bot processes)
```

**1.4 RESTART BOTS**
```
Menu: 🔄 Restart
Expected:
  ✅ Bots stop
  ✅ Wait 3 seconds
  ✅ Bots start again
  ✅ "ALL SYSTEMS ONLINE" alert
  ✅ Status shows all ALIVE
```

---

### Phase 2: Trading Mode Management (5 minutes)

**2.1 SWITCH TO PAPER MODE**
```
Menu: 🎮 Trading Mode → 🎭 PAPER
Expected:
  ✅ Config updates: mode = PAPER
  ✅ Status shows: PAPER MODE ACTIVE
  ✅ Trades use simulated_trades table
  ✅ No real money at risk
Verify: grep "mode" config/trading_v3_artem.json
```

**2.2 SWITCH TO REAL MODE**
```
Menu: 🎮 Trading Mode → 💰 REAL
Expected:
  ⚠️ Confirmation prompt shows
  ⚠️ Warning about real money
  ✅ Click confirm
  ✅ Config updates: mode = REAL
  ✅ Status shows: REAL MODE ACTIVE
  ✅ Trades use real_trades table
Verify: grep "mode" config/trading_v3_artem.json
```

**2.3 CHECK TRADING MODE**
```
Menu: 🎮 Trading Mode → 📊 Current Mode
Expected:
  ✅ Shows current mode (PAPER or REAL)
  ✅ Shows corresponding table (simulated_trades or real_trades)
```

---

### Phase 3: Risk Management Configuration (10 minutes)

**3.1 CONSERVATIVE RISK SETTINGS**
```
Menu: ⚙️ Settings → 💰 CONSERVATIVE Risk
Expected:
  ✅ Shows current CONSERVATIVE risk value
  ✅ Prompts to enter new value
  ✅ Accepts: $0.10, $0.25, $0.50, $1.00
  ✅ Updates in database
Verify: Control Bot shows new value on next STATUS check
```

**3.2 TREND RISK SETTINGS**
```
Menu: ⚙️ Settings → 📈 TREND Risk
Expected:
  ✅ Shows current TREND risk value
  ✅ Prompts to enter new value
  ✅ Accepts: $5.00, $10.00, $25.00, $50.00
  ✅ Updates in database
Verify: Control Bot shows new value on next STATUS check
```

**3.3 TP LEVELS CONFIGURATION**
```
Menu: ⚙️ Settings → 🎯 TP Levels
Expected:
  ✅ Shows current TP percentages
  ✅ Allows editing: TP1, TP2, TP3 percentages
  ✅ Updates immediately
Verify: Next trade shows updated TP levels
```

**3.4 LEVERAGE SETTING**
```
Menu: ⚙️ Settings → 🔧 Leverage
Expected:
  ✅ Shows current leverage (1x, 5x, 10x, etc.)
  ✅ Accepts new leverage value
  ✅ Updates in config
Verify: Config file shows new leverage
```

**3.5 SL ATR MULTIPLIER**
```
Menu: ⚙️ Settings → 🔧 SL ATR %
Expected:
  ✅ Shows current: 10%, 15%, or 20%
  ✅ Allows switching between options
  ✅ Updates immediately
Verify: Next trade SL distance matches multiplier × ATR
```

---

### Phase 4: Signal Bot Parameter Tuning (10 minutes)

**4.1 SIGNAL BOT PARAMETERS**
```
Menu: ⚙️ Settings → 🔍 Signal Bot Parameters
Expected:
  ✅ Sub-menu opens with 3 options
```

**4.2 VOLUME THRESHOLD**
```
Menu: Signal Bot Parameters → 📊 Volume ($)
Current: $100,000
Expected:
  ✅ Shows current value
  ✅ Accepts new threshold
  ✅ Updates signal generation
Verify: Only signals with volume > threshold appear
```

**4.3 SPIKE RATIO THRESHOLD**
```
Menu: Signal Bot Parameters → 📈 Spike Ratio
Current: 2.0x
Expected:
  ✅ Shows current value
  ✅ Accepts new multiplier (1.5x, 2.0x, 2.5x, 3.0x)
  ✅ Updates signal generation
Verify: Only signals with spike > ratio appear
```

**4.4 BUY/SELL VOLUME RATIO**
```
Menu: Signal Bot Parameters → 💰 B/S Ratio
Current: 1.0x
Expected:
  ✅ Shows current value
  ✅ Accepts new ratio (0.8x, 1.0x, 1.2x)
  ✅ Updates signal quality
Verify: Signal selection matches new ratio criteria
```

---

### Phase 5: Monitoring & Statistics (10 minutes)

**5.1 OPEN POSITIONS**
```
Menu: 📍 Positions
Expected:
  ✅ Lists all open positions
  ✅ Shows: Symbol, Entry, Current, P&L, SL, TP
  ✅ Updates in real-time
```

**5.2 RECENT SIGNALS**
```
Menu: 📡 Signals
Expected:
  ✅ Shows last 10 signals
  ✅ Shows: Symbol, Entry, Spike, Volume, Direction
  ✅ Marks processed vs pending
```

**5.3 STATISTICS**
```
Menu: 📊 Statistics
Expected:
  ✅ Shows: Win Rate, Total Trades, P&L
  ✅ Shows: Open positions, Closed trades
  ✅ Updates every time clicked
Verify: Numbers match database
```

**5.4 TRADING LOG**
```
Menu: 📋 Logs
Expected:
  ✅ Shows recent bot activity
  ✅ Shows errors and important events
  ✅ Scrollable (last 100 lines)
```

**5.5 STRATEGY STATUS**
```
Menu: 🎯 Current Strategy
Expected:
  ✅ Shows current strategy: CONSERVATIVE or TREND
  ✅ Shows TP3 rate (for auto-switching)
  ✅ Shows win rate threshold
  ✅ Shows next check time
```

---

### Phase 6: Database Management (5 minutes)

**6.1 CLEAN DATABASE**
```
Menu: ⚙️ Settings → 🔄 Clean Database
Expected:
  ⚠️ Confirmation prompt
  ✅ Lists what will be cleared
  ✅ Click: ✅ YES, CLEAN IT
  ✅ Database clears (15 tables)
  ✅ Confirmation: "DATABASE CLEANED"
Verify: 
  - No positions in Positions menu
  - No signals in Signals menu
  - Statistics reset to 0
```

---

### Phase 7: Code Management (5 minutes)

**7.1 UPDATE CODE FROM GIT**
```
Menu: ⚙️ Settings → 📦 Update Code
Expected:
  ✅ "Pulling latest code..." message
  ✅ Shows old commit hash
  ✅ Shows new commit hash
  ✅ Confirmation: "CODE UPDATED SUCCESSFULLY"
  ✅ Recommendation to restart bots
Verify: git log | head -1 shows new commit
```

**7.2 RESTART AFTER UPDATE**
```
Menu: 🔄 Restart (after code update)
Expected:
  ✅ Bots stop
  ✅ Bots load NEW code
  ✅ New features/fixes available
  ✅ "ALL SYSTEMS ONLINE" alert
```

---

### Phase 8: Data Export (5 minutes)

**8.1 SUMMARY REPORT**
```
Menu: 📤 Export → 📋 Summary Report → Select Period
Expected:
  ✅ Shows report for selected period
  ✅ Includes: Trades, Win Rate, P&L, Statistics
  ✅ Formatted for viewing
```

**8.2 CSV DOWNLOAD**
```
Menu: 📤 Export → 📥 Download CSV → Select Period
Expected:
  ✅ Exports trades data to CSV
  ✅ Can download and analyze in Excel
  ✅ Includes all trade details
```

---

### Phase 9: Critical Functions Test (15 minutes)

**9.1 RULE ENFORCEMENT: 1 Position per Symbol**
```
Steps:
1. Start bots (PAPER mode)
2. Create signal manually for DOGEUSDT
3. Verify position opens
4. Create ANOTHER signal for DOGEUSDT
5. VERIFY: Second signal is REJECTED

Expected:
  ✅ Second signal shows: "REJECTED: DOGEUSDT already has 1 open position"
  ✅ No duplicate position created
  ✅ System enforces 1 position per symbol rule
```

**9.2 SL/TP PROTECTION: Auto-Close if SL Fails**
```
Steps:
1. Start bots (PAPER mode)
2. Create signal
3. Monitor order execution
4. IF SL setup fails → position auto-closes

Expected:
  ✅ Order opens successfully
  ✅ SL sets successfully
  ✅ IF SL fails → position closes automatically
  ✅ No unprotected positions remain
```

**9.3 TP/SL CLEANUP: No Accumulation**
```
Steps:
1. Create multiple signals
2. Monitor TP/SL setup
3. Check position has correct TP/SL only

Expected:
  ✅ Old TP/SL cleared before new setup
  ✅ No accumulation (21+ TP orders)
  ✅ Only current TP/SL active
  ✅ Respects ByBit 20-limit
```

**9.4 TRADING MODE AUTO-SWITCH**
```
Steps:
1. Start in CONSERVATIVE mode (PAPER)
2. Wait for TP3 rate to exceed 35%
3. System automatically switches to TREND (REAL)
4. When TP3 rate drops below 30% → back to CONSERVATIVE (PAPER)

Expected:
  ✅ Mode switches automatically based on win rate
  ✅ Strategy changes from CONSERVATIVE to TREND
  ✅ Mode changes from PAPER to REAL
  ✅ Alerts show strategy/mode changes
```

---

### Phase 10: Health & Reliability (20 minutes)

**10.1 BOT RESTART RESILIENCE**
```
Steps:
1. Stop bots
2. Wait 5 seconds
3. Restart bots
4. Check status every 10 seconds for 2 minutes

Expected:
  ✅ Bots start cleanly
  ✅ No error messages
  ✅ All systems online within 60 seconds
  ✅ Existing positions still visible
  ✅ Statistics preserved
```

**10.2 SIGNAL GENERATION CONTINUITY**
```
Steps:
1. Start bots (PAPER mode)
2. Wait 5 minutes
3. Check Signals menu
4. Should see new signals

Expected:
  ✅ Signals continue generating
  ✅ Each signal has valid: Entry, SL, TP, Volume, Spike
  ✅ No gaps in signal generation
  ✅ Spike calculations correct
```

**10.3 POSITION MONITORING**
```
Steps:
1. Open a position (manual signal or real)
2. Wait 5 minutes
3. Monitor position in Positions menu
4. Check price updates in real-time

Expected:
  ✅ Position price updates every 5-30 seconds
  ✅ Current P&L calculated correctly
  ✅ SL/TP levels visible and correct
  ✅ Position shows correct side (LONG/SHORT)
```

**10.4 CRITICAL ALERTS**
```
Steps:
1. Run system for 10 minutes
2. Monitor Telegram alerts
3. Expect:
   - Bot startup alerts (3 bots)
   - Statistics every hour
   - Trade open/close alerts (if trading)

Expected:
  ✅ No error alerts unless actual issue
  ✅ Regular statistics reports
  ✅ Trade alerts on order execution
  ✅ Timestamp on all alerts
```

---

## 📊 SCORING SYSTEM

**Pass Criteria:**
- ✅ All Phase 1-8 tests pass = 80% pass
- ✅ All Phase 9 critical tests pass = 95% pass
- ✅ All Phase 10 health tests pass = 100% pass

**Acceptable Failures:**
- Network-related (WebSocket timeout)
- API-related (ByBit rate limit)
- Time-based (statistics not yet updated)

**CRITICAL Failures (Stop System):**
- Duplicate positions on same symbol
- Unprotected positions (no SL)
- Data corruption (negative stats)
- Control Bot unresponsive

---

## 🎯 SUCCESS CRITERIA

System is AUTONOMOUS when:

✅ **All bot lifecycle functions work** (Start, Stop, Restart)  
✅ **All parameters changeable** (Risk, TP, Leverage, SL, Signal params)  
✅ **All monitoring functions work** (Positions, Signals, Statistics, Logs)  
✅ **All critical rules enforced** (1 position per symbol, SL protection)  
✅ **All data management works** (Clean DB, Export CSV)  
✅ **Code updates via Control Bot** (Git pull, auto-restart)  
✅ **Bots resilient to restart** (No data loss, clean startup)  
✅ **NO external assistance needed** (All via Control Bot)  

---

## 📝 TESTING LOG TEMPLATE

```markdown
# AUTONOMY TEST LOG - [DATE] [TIME UTC]

## Test Environment
- Mode: PAPER / REAL
- Strategy: CONSERVATIVE / TREND
- Risk Level: $X
- Network: VPN Connected / Direct

## Phase 1: Lifecycle
- [ ] START BOTS - PASS / FAIL
- [ ] STATUS CHECK - PASS / FAIL
- [ ] STOP BOTS - PASS / FAIL
- [ ] RESTART BOTS - PASS / FAIL

## Phase 2: Trading Mode
- [ ] SWITCH PAPER - PASS / FAIL
- [ ] SWITCH REAL - PASS / FAIL
- [ ] MODE CHECK - PASS / FAIL

## Phase 3-10: [Continue for all phases]

## Critical Issues Found
[List any failures]

## Overall Status
PASS / FAIL

## Signature
Tested by: [Name]
Date: [YYYY-MM-DD HH:MM UTC]
```

---

## 🚀 NEXT STEPS

1. **Print this document** or view on Control Bot screen
2. **Start fresh test** (Clean DB first)
3. **Work through each phase** sequentially
4. **Mark PASS/FAIL** for each test
5. **Document any issues** found
6. **Report results** to Artem

---

**GOAL:** Prove that system works 100% independently via Control Bot.  
**CONFIDENCE:** After passing all tests, you can manage system WITHOUT Dex.  
**TIME ESTIMATE:** 90 minutes for complete autonomy verification.

---

*Document created: 2026-04-03 23:09 UTC*  
*Last verified: [To be filled during testing]*
