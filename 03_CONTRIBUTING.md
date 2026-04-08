# 🔨 Contributing to 4BotsBybit

**Guidelines for developing, testing, and deploying changes.**

---

## Git Workflow

### Branches

```
main/
├─ develop              # Current development version (production-ready)
└─ feature/xxx          # Feature branches (temporary)
```

### Commit Convention

```
Type: Message

Types:
✨ FEATURE:   New functionality
🔧 FIX:       Bug fix
⚙️  TUNING:    Parameter adjustment
📊 REFACTOR:  Code reorganization
📝 DOCS:      Documentation
🔒 SECURITY:  Security improvement
🚀 PERF:      Performance optimization
```

**Examples:**
```
git commit -m "✨ FEATURE: Add signal filtering by volume"
git commit -m "🔧 FIX: Correct TP close_reason calculation"
git commit -m "⚙️ TUNING: Reduce B/S threshold from 2.0x to 1.0x"
```

---

## Code Standards

### Safety Rules (CRITICAL!)

#### Rule #1: Dual-Mode Checking
```python
# ❌ WRONG - only checks PAPER mode
cursor.execute("SELECT * FROM simulated_trades WHERE status='open'")

# ✅ CORRECT - checks both modes
mode = 'REAL' if self.current_trading_mode == 'REAL' else 'PAPER'
trades_table = 'real_trades' if mode == 'REAL' else 'simulated_trades'
cursor.execute(f"SELECT * FROM {trades_table} WHERE status='open'")
```

#### Rule #2: Process Restart After Code Changes
```python
# Code changes require FULL process restart
# Python caches modules in memory!

# ✗ Just changing the file is NOT enough
# ✓ Must kill process and let systemd restart it
# ✓ OR manually: pkill -9 python3 && systemctl restart service
```

#### Rule #3: Logging Levels
```python
# Use INFO for user-visible features
logger.info("✨ Signal detected: BTCUSDT LONG")

# Use DEBUG for internal tracing
logger.debug("ATR calculation: 0.0234")

# Use WARNING for important alerts
logger.warning("⚠️ Uncommitted changes detected!")

# Use ERROR for failures
logger.error("❌ Failed to create position")
```

#### Rule #4: B/S Volume Calculation
```python
# ALWAYS calculate from 5-bar AVERAGE (not last bar, not orderbook!)

# ✗ WRONG - only last candle
buy_vol = klines[-1]['buyVolume']

# ✗ WRONG - from orderbook (doesn't match Total Volume)
buy_vol = orderbook_bids_sum

# ✓ CORRECT - 5-bar average
buy_volumes = [k['buyVolume'] for k in klines[-5:]]
avg_buy = sum(buy_volumes) / len(buy_volumes)
```

---

## Testing Requirements

### Before Committing:

```bash
# 1. Test in PAPER mode first
systemctl restart bybit-control-bot.service
# Wait 60 seconds
# Manually test START/STOP/UPDATE CODE

# 2. Verify no process duplicates
ps aux | grep python3 | grep -E "signal_bot|trading_bot|strategy_switcher"
# Should show EXACTLY 1 process each (during operation)

# 3. Check logs for errors
tail -50 logs/signal_bot_v3.log | grep ERROR
tail -50 logs/trading_bot_v3.log | grep ERROR
tail -50 logs/control_bot_v3.log | grep ERROR
# Should be EMPTY (or only old errors)

# 4. Verify git status
git status
# Should be CLEAN (no uncommitted changes before merge)
```

---

## Code Review Checklist

Before pushing to develop:

- [ ] Code compiles without syntax errors
- [ ] Follows dual-mode safety rule for PAPER + REAL modes
- [ ] Logging is appropriate level (not DEBUG for user features)
- [ ] No hardcoded credentials or sensitive data
- [ ] Process restart handled if needed
- [ ] Commit message follows convention
- [ ] Tests passed in PAPER mode
- [ ] No process duplicates created
- [ ] Database queries handle both trades tables

---

## Deployment Process

### Step 1: Develop & Test
```bash
# Make changes in develop branch
git checkout develop
# ... edit code ...

# Test thoroughly in PAPER mode
systemctl restart bybit-control-bot.service
# Verify no errors for at least 5 minutes
```

### Step 2: Commit
```bash
git add .
git commit -m "✨ FEATURE: Description of change"
```

### Step 3: Push to GitHub
```bash
git push origin develop
```

### Step 4: Deploy (via Control Panel)
```
Telegram → Settings → 📦 Update Code
# Git pulls latest from GitHub
# Shows new commit hash

Telegram → 🔄 Restart
# Kills old processes
# Loads new code
# Starts fresh
```

---

## Emergency Procedures

### If Code Breaks Trading:

```bash
# 1. IMMEDIATELY stop all bots
systemctl stop bybit-control-bot.service
pkill -9 python3

# 2. Revert to last known good version
git log --oneline | head -5
git checkout [GOOD_COMMIT_HASH]

# 3. Restart
systemctl start bybit-control-bot.service

# 4. Notify about rollback
```

### If Signal Bot Crashes Repeatedly:

```bash
# 1. Check for process duplicates
ps aux | grep signal_bot | wc -l
# If > 1, kill them: pkill -9 -f telegram_bot_runner_v3

# 2. Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 3. Check latest commit
git log --oneline -1

# 4. Restart fresh
systemctl restart bybit-control-bot.service
```

---

## Performance Optimization

### Before/After Benchmarks:

Always measure impact:
```bash
# Memory before change
ps aux | grep signal_bot | awk '{print $6}'  # 180MB?

# After change - should not increase significantly
ps aux | grep signal_bot | awk '{print $6}'  # Still ~180MB?
```

### Common Issues:

```
High CPU (>50%) → Check nested loops, optimize calculations
High Memory (>300MB) → Check for memory leaks, websocket backlog
High Log Size (>1GB) → Reduce logging verbosity, rotate logs
```

---

## Git Commands Reference

```bash
# Setup (first time)
git clone https://github.com/InfinitySudo/4BotsBybit.git
cd 4BotsBybit

# Daily workflow
git status                    # See changes
git add .                     # Stage everything
git commit -m "message"       # Commit
git push origin develop       # Push to GitHub

# If need to undo
git reset --hard HEAD~1       # Undo last commit (CAREFUL!)
git revert HEAD               # Create "undo" commit (safer)

# Check history
git log --oneline -10         # Last 10 commits
git diff HEAD~1               # Changes since last commit
git show COMMIT_HASH          # See specific commit
```

---

## Questions?

Check:
1. Code comments (inline explanations)
2. logs/ directory (error messages)
3. README.md (overview)
4. Git history (what changed and why)

---

**Last Updated:** 2026-04-02  
**Maintained by:** InfinitySudo
