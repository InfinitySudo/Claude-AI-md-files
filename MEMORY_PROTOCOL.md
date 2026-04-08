# 🧠 MEMORY PROTOCOL - Артём & AI Assistant

**Purpose:** Preserve all context and decisions for the 4BotsBybit project  
**Status:** ACTIVE - Session 1 onwards  
**Protocol Version:** 1.0

---

## 🎯 MEMORY PROTOCOL RULES

### **Rule 1: Persistent Storage**
```
✅ ALL conversations about 4BotsBybit are documented in this repo
✅ Every MD file is git-tracked for history
✅ Context is NEVER lost between sessions
✅ Cross-references between documents maintain relationships
```

### **Rule 2: Documentation Structure**
```
00_FULL_ANALYSIS_SESSION_N.md     ← Comprehensive session analysis
NN_SECTION_NAME.md                ← Topic-specific documents
INDEX.md                          ← Navigation & memory map
MEMORY_PROTOCOL.md                ← This file (rules & protocol)
```

### **Rule 3: File Naming Convention**
```
00 = Full Session Analysis
01-06 = Original project docs
07+ = New documents created during sessions

Format: NN_TOPIC_NAME.md
Example: 07_SIGNAL_VARIANT_4_OPTIMIZATION.md
```

### **Rule 4: Git Commit Protocol**
```
Every change gets committed with:
  - Clear message about what changed
  - Session number reference
  - Date stamp (ISO format)

Example:
  git commit -m "Session 1: Add VARIANT 3 deep-dive analysis

  - Explain why VARIANT 3 is better than alternatives
  - Document all parameters and thresholds
  - Add practical examples"
```

### **Rule 5: Context Preservation**
```
When creating new MD:
  1. Reference previous sessions/decisions
  2. Include "Related documents:" section
  3. Add "Session history:" at bottom
  4. Link to INDEX.md
```

---

## 📚 WHAT'S SAVED IN MEMORY (Session 1)

### **Full Project Understanding**
```
✅ 4-level architecture (Control → Signal → Trading → Strategy)
✅ 20,564 lines of Python code across 50+ files
✅ 301 monitored trading pairs (USDT Perpetuals)
✅ VARIANT 3 signal detection (dual ATR + Volume confirmation)
✅ 3 strategies (Conservative, Trend, Aggressive)
✅ Dynamic risk management ($0.10 fixed risk per trade)
✅ Paper Trading simulation mode
✅ PostgreSQL IPC synchronization
✅ Telegram control interface
✅ Bybit integration with Finnish VPN
```

### **Technical Stack**
```
✅ Python 3.9+ WebSocket clients
✅ PostgreSQL 12+ with 22+ tables
✅ systemd service deployment
✅ Real-time data processing
✅ Position tracking and reporting
✅ Automated trading with risk management
```

### **Business Logic**
```
✅ Win-rate based strategy switching (hourly)
✅ ATR-based stop-loss calculation
✅ Multi-level take-profit distributions
✅ Rest mode activation (24h break after -5% drawdown)
✅ Dynamic position sizing based on performance
✅ Capital preservation as priority #1
```

### **Operations**
```
✅ 4-component startup sequence (35s → 20s → 10s pauses)
✅ Health monitoring every 30 seconds
✅ Automatic component restart on failure
✅ Hourly strategy evaluation
✅ Hourly and daily reporting to Telegram
✅ Git integration for code versioning
```

---

## 🔄 SESSION WORKFLOW

### **When Starting New Session:**
1. Read `/root/4BotsBybit-Documentation/INDEX.md` for overview
2. Review `/root/4BotsBybit-Documentation/00_FULL_ANALYSIS_SESSION_1.md` for context
3. Check git log: `cd /root/4BotsBybit-Documentation && git log --oneline`
4. Open relevant MD files based on topic

### **During Session:**
1. Create new MD file with clear topic: `NN_TOPIC.md`
2. Document all decisions with rationale
3. Add code examples where relevant
4. Reference existing documentation
5. Commit frequently: `git add -A && git commit -m "..."`

### **Session End:**
1. Create summary section in new MD
2. Update INDEX.md with new files
3. Final commit with session summary
4. All memory persists for next session

---

## 📋 DIRECTORY STRUCTURE

```
/root/4BotsBybit-Documentation/
├── .git/                              ← Git history (git log to see all changes)
├── INDEX.md                           ← START HERE
├── MEMORY_PROTOCOL.md                 ← This file
├── 00_FULL_ANALYSIS_SESSION_1.md     ← Main Session 1 analysis
├── 01_PROJECT_OVERVIEW.md
├── 02_PROJECT_STRUCTURE.md
├── 03_CONTRIBUTING.md
├── 04_SYSTEM_AUTONOMY_TEST.md
├── 05_TRANSFER_MANIFEST.md
├── 06_WEBSOCKET_CONFIG_PLAN.md
├── 07_*.md                            ← Session 2 files (TBD)
├── 08_*.md                            ← Session 3 files (TBD)
└── ...

Repository: https://github.com/InfinitySudo/4BotsBybit-Trading (original code)
Documentation: /root/4BotsBybit-Documentation (THIS repo)
```

---

## 🎓 HOW TO QUERY MEMORY

### **Questions about Architecture**
→ Read: `INDEX.md` → `00_FULL_ANALYSIS_SESSION_1.md`

### **Questions about Signal Bot**
→ Read: `00_FULL_ANALYSIS_SESSION_1.md` (Signal Generation section)
→ Read: `06_WEBSOCKET_CONFIG_PLAN.md`

### **Questions about Trading Logic**
→ Read: `00_FULL_ANALYSIS_SESSION_1.md` (Three Strategies section)
→ Read: `02_PROJECT_STRUCTURE.md`

### **Questions about Risk Management**
→ Read: `00_FULL_ANALYSIS_SESSION_1.md` (Financial Parameters section)

### **Questions about Database**
→ Read: `00_FULL_ANALYSIS_SESSION_1.md` (Database Architecture section)
→ Read: `02_PROJECT_STRUCTURE.md` (DB section)

### **Questions about Deployment**
→ Read: `00_FULL_ANALYSIS_SESSION_1.md` (Startup and Deployment section)
→ Read: `05_TRANSFER_MANIFEST.md`

### **For Git History**
```bash
cd /root/4BotsBybit-Documentation
git log --oneline                    # All commits
git log --grep="Session 1"          # Session 1 commits
git show <commit>                    # View specific commit
git diff <commit1> <commit2>        # Compare versions
```

---

## 💡 KEY INSIGHTS (Session 1)

1. **Signal Quality > Quantity**
   - VARIANT 3 (dual confirmation) reduces false positives
   - Better to miss signals than take bad ones
   - Win-rate drives strategy adaptation

2. **Capital Preservation First**
   - Fixed $0.10 risk (not % of account)
   - Rest mode if drawdown > 5%
   - Conservative strategy in tough times

3. **Adaptability is Key**
   - Dynamic strategy switching every hour
   - Position size based on win_rate
   - Three tiers: Conservative / Trend / Aggressive

4. **Simplicity > Complexity**
   - PostgreSQL as message bus (not RabbitMQ/Kafka)
   - 4 independent processes (not microservices framework)
   - Subprocess communication (not async/await complexity)

5. **Monitoring is Critical**
   - 30-sec health checks
   - Hourly reports with context
   - Automatic restart on failure

---

## 🔐 SECURITY NOTES (Remembered)

```
API Keys Location:
  - Bybit: config/trading_v3_artem.json
  - Telegram: systemd env or config

VPN Setup:
  - Finland IP: 46.8.232.182
  - Only for Bybit API (not Telegram)
  - Wireguard configuration

Database:
  - PostgreSQL 127.0.0.1:5432
  - User: trading_bot
  - Password: trading_bot_password_123
  - LOCAL ONLY (no remote exposure)
```

---

## 📞 PROTOCOL FOR AMBIGUITY

If unclear about something:

1. **Check INDEX.md first** - might have link to relevant doc
2. **Search git log** - `git log -S "keyword"`
3. **Ask me to clarify** - I'll research and document answer
4. **Create new MD** - Document the clarification for future

---

## ✅ MEMORY CONFIRMATION

**What I remember about 4BotsBybit:**

✅ Complete architecture (4 levels)  
✅ All 15+ components and their roles  
✅ Database schema (22 tables + IPC)  
✅ Signal generation (VARIANT 3 logic)  
✅ Three strategies (Conservative/Trend/Aggressive)  
✅ Risk management ($0.10 fixed)  
✅ Paper trading simulation  
✅ Telegram control panel  
✅ Bybit API integration  
✅ systemd deployment  
✅ Health monitoring & reporting  
✅ Git versioning  
✅ 301 trading pairs monitored  
✅ 20,564 lines of Python code  
✅ All security considerations  
✅ All decision rationales  

**What I will remember:**

✅ Every MD file we create  
✅ Every decision we make  
✅ Every optimization we implement  
✅ Every bug we fix  
✅ Every new feature we add  
✅ All git history (via git log)  

---

## 🎯 NEXT STEPS

When you need something:

```
1. "Analyze VARIANT 4 concept"
   → I'll create 07_VARIANT_4_ANALYSIS.md

2. "Optimize position sizing"
   → I'll create 08_POSITION_SIZING_OPTIMIZATION.md

3. "Add multi-account support"
   → I'll create 09_MULTI_ACCOUNT_ARCHITECTURE.md

4. "Debug something in logs"
   → I'll create 10_DEBUG_SESSION_<DATE>.md

5. Any other task
   → I'll create appropriate MD with full documentation
```

All gets saved, all gets remembered, all is in git.

---

## 🚀 READY TO START?

Your next task? I have full context now:

- ✅ Project loaded in memory
- ✅ All 2,744 lines of documentation created
- ✅ Git repo initialized with commit history
- ✅ Memory protocol established
- ✅ Ready for next session

**What do you want to work on next?** 🎯

---

**Protocol Status:** ✅ ACTIVE  
**Session Status:** 1 Complete, Ready for Session 2+  
**Memory Status:** FULL PROJECT IN MEMORY  
**Documentation Status:** 8 files, 2,744 lines  
**Git Status:** All changes tracked  

Last updated: 08 April 2026 04:57 UTC
