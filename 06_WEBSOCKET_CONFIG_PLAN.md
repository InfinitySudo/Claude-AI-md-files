# 🎯 WebSocket Configuration Implementation Plan

**Purpose:** Add dynamic configuration for ATR bars and signal volume bars WITHOUT breaking existing system.

**Created:** 2026-04-03 23:41 UTC  
**Status:** PLANNING PHASE

---

## 📋 REQUIREMENTS

### Current Hardcoded Values (to be parameterized)

```python
# 1. ATR Calculation
   - Daily ATR uses: 15 daily bars
   - Need to make configurable: 5-20 bars

# 2. Volume Average (for spike detection)
   - Current: Uses 5 bars total
   - Takes first 4 bars as HISTORY: avg = sum(bar[0:4]) / 4
   - Takes 5th bar as CURRENT: current = bar[4]
   - Need to make configurable: 3-10 bars total

# 3. 5m Trend Calculation
   - Current: Uses last 5 bars: klines_5m[-5:]
   - Need to make configurable: 3-10 bars

# 4. Trend Direction Logic
   - Current: Hardcoded in _calculate_5m_trend()
   - Need flexible threshold
```

---

## 🔧 IMPLEMENTATION STRATEGY

### STEP 1: Add Configuration Parameters (NO CODE CHANGE YET)

**File:** `config/trading_v3_artem.json`

Add new section:
```json
{
  "signal_bot": {
    "websocket_config": {
      "atr_daily_bars": 15,
      "volume_avg_bars": 5,
      "trend_bars": 5,
      "spike_threshold_x": 2.0,
      "volume_threshold_usd": 100000,
      "bs_ratio_threshold": 1.0
    }
  }
}
```

### STEP 2: Load Config in Signal Bot (MINIMAL IMPACT)

**File:** `src/signal_bot_v3_websocket.py` - Line 50 (in __init__)

```python
# Load configuration
self.config = self._load_websocket_config()

def _load_websocket_config(self) -> Dict:
    """Load WebSocket parameters from config file"""
    try:
        config_file = "/root/4botsBybit-production/config/trading_v3_artem.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Get WebSocket config with defaults
        ws_config = config.get('signal_bot', {}).get('websocket_config', {})
        return {
            'atr_daily_bars': ws_config.get('atr_daily_bars', 15),
            'volume_avg_bars': ws_config.get('volume_avg_bars', 5),
            'trend_bars': ws_config.get('trend_bars', 5),
            'spike_threshold_x': ws_config.get('spike_threshold_x', 2.0),
            'volume_threshold_usd': ws_config.get('volume_threshold_usd', 100000),
            'bs_ratio_threshold': ws_config.get('bs_ratio_threshold', 1.0)
        }
    except Exception as e:
        self.logger.error(f"Error loading WebSocket config: {e}")
        # Return defaults if config fails
        return {
            'atr_daily_bars': 15,
            'volume_avg_bars': 5,
            'trend_bars': 5,
            'spike_threshold_x': 2.0,
            'volume_threshold_usd': 100000,
            'bs_ratio_threshold': 1.0
        }
```

### STEP 3: Replace Hardcoded Values (CRITICAL - ONE BY ONE)

#### Change 1: ATR Daily Bars (Line 116)

**BEFORE:**
```python
klines = self.api.get_klines(symbol, interval='D', limit=15)
```

**AFTER:**
```python
klines = self.api.get_klines(symbol, interval='D', limit=self.config['atr_daily_bars'])
```

#### Change 2: Volume Average Bars (Line 234)

**BEFORE:**
```python
closed_klines = klines_5m[-5:] if len(klines_5m) >= 5 else klines_5m
if len(closed_klines) < 5:
    self.logger.debug(f"❌ {symbol}: Недостаточно свечей ({len(closed_klines)}<5)")
    return None
```

**AFTER:**
```python
bars_needed = self.config['volume_avg_bars']
closed_klines = klines_5m[-bars_needed:] if len(klines_5m) >= bars_needed else klines_5m
if len(closed_klines) < bars_needed:
    self.logger.debug(f"❌ {symbol}: Недостаточно свечей ({len(closed_klines)}<{bars_needed})")
    return None
```

#### Change 3: Volume Calculation (Line 259)

**BEFORE:**
```python
avg_volume = sum(volumes[:4]) / 4 if len(volumes) >= 4 else (sum(volumes) / len(volumes) if volumes else 0)
current_volume = volumes[4] if len(volumes) > 4 else (volumes[-1] if volumes else 0)
```

**AFTER:**
```python
bars_for_avg = self.config['volume_avg_bars'] - 1  # n-1 bars for history
avg_volume = sum(volumes[:bars_for_avg]) / bars_for_avg if len(volumes) > bars_for_avg else (sum(volumes[:-1]) / (len(volumes)-1) if len(volumes) > 1 else 0)
current_volume = volumes[-1] if volumes else 0  # Always use LAST bar as current
```

#### Change 4: Trend Bars (Line 281)

**BEFORE:**
```python
trend = self._calculate_5m_trend(klines_5m[-5:])
```

**AFTER:**
```python
trend = self._calculate_5m_trend(klines_5m[-self.config['trend_bars']:])
```

#### Change 5: Update _calculate_5m_trend Method (Line 369)

**BEFORE:**
```python
def _calculate_5m_trend(self, klines_5m: List[Dict]) -> str:
    """Вычислить тренд за последние 5 5m свечей"""
    if not klines_5m or len(klines_5m) < 3:
        return "UNKNOWN"
    
    # Use first and last close
    first_close = float(klines_5m[0].get('close', 0))
    last_close = float(klines_5m[-1].get('close', 0))
```

**AFTER:**
```python
def _calculate_5m_trend(self, klines_5m: List[Dict]) -> str:
    """Вычислить тренд за последние N 5m свечей (N = config['trend_bars'])"""
    bars_needed = self.config['trend_bars']
    if not klines_5m or len(klines_5m) < 3:  # Always need at least 3
        return "UNKNOWN"
    
    # Use first and last close from available bars
    first_close = float(klines_5m[0].get('close', 0))
    last_close = float(klines_5m[-1].get('close', 0))
```

---

## 🛡️ SAFETY MEASURES

### Constraint 1: Minimum Bars
```python
# Don't allow less than 3 bars for any calculation
def _validate_config(self):
    """Validate config bounds"""
    self.config['atr_daily_bars'] = max(5, min(self.config['atr_daily_bars'], 50))
    self.config['volume_avg_bars'] = max(3, min(self.config['volume_avg_bars'], 10))
    self.config['trend_bars'] = max(3, min(self.config['trend_bars'], 10))
```

### Constraint 2: Backward Compatibility
```python
# If config missing, use ORIGINAL defaults
# This prevents breaking if someone updates without updating config
defaults = {
    'atr_daily_bars': 15,      # Original
    'volume_avg_bars': 5,       # Original
    'trend_bars': 5,            # Original
}
```

### Constraint 3: Hot Reload (NO RESTART NEEDED)
```python
# Reload config on every signal check (minimal overhead)
def _check_signal(self, ...):
    self.config = self._load_websocket_config()  # Reload fresh
    ...
```

---

## 📊 CONTROL BOT INTEGRATION

### Add New Settings Menu Option

**File:** `src/control_bot_simple_v3.py`

Add button in Settings menu:
```python
[{'text': '📡 WebSocket Parameters', 'callback_data': 'set_websocket_params'}]
```

### Sub-menu: WebSocket Settings

```
🔧 WebSocket Settings:
├─ 📊 ATR Daily Bars (currently: 15, range: 5-50)
├─ 📈 Volume Avg Bars (currently: 5, range: 3-10)
├─ 📉 Trend Bars (currently: 5, range: 3-10)
├─ 🎯 Spike Threshold (currently: 2.0x, range: 1.0-5.0)
└─ ◀️ Back
```

### Implementation in Control Bot

```python
elif data == "set_websocket_params":
    """Open WebSocket settings menu"""
    text = "📡 <b>WEBSOCKET SETTINGS</b>\n\nConfigure signal generation parameters:"
    keyboard = {
        'inline_keyboard': [
            [{'text': '📊 ATR Bars', 'callback_data': 'set_atr_bars'}],
            [{'text': '📈 Volume Avg Bars', 'callback_data': 'set_volume_bars'}],
            [{'text': '📉 Trend Bars', 'callback_data': 'set_trend_bars'}],
            [{'text': '🎯 Spike Threshold', 'callback_data': 'set_spike_threshold'}],
            [{'text': '◀️ Back', 'callback_data': 'settings'}]
        ]
    }
    self.edit_message(chat_id, message_id, text, keyboard)

elif data == "set_atr_bars":
    """Set ATR daily bars"""
    text = "📊 <b>ATR DAILY BARS</b>\n\nCurrent: 15\n\nSelect new value (5-50):\nEnter number:"
    # ... prompt for input
```

---

## 🧪 TESTING STRATEGY

### Test 1: Default Behavior (NOTHING CHANGES)
```
1. Don't modify config file
2. Start Signal Bot
3. Verify signals still work exactly as before
4. Expected: Spike ratios same, trends same, volume thresholds same
```

### Test 2: Increase Volume Bars from 5 to 7
```
1. Update config: "volume_avg_bars": 7
2. Restart Signal Bot
3. Signals should now use 7 bars for average (first 6, current 7th)
4. Spike ratios should change (smoother, less volatile)
```

### Test 3: Decrease Trend Bars from 5 to 3
```
1. Update config: "trend_bars": 3
2. Restart Signal Bot
3. Trend calculation should be faster (less history needed)
4. Signals may appear quicker
```

### Test 4: Hot Reload (NO RESTART)
```
1. Signal Bot running with default config
2. Change config file while Signal Bot running
3. Next signal should use NEW config values
4. NO restart or restart_bots needed!
```

---

## 📈 EXPECTED IMPACTS

| Parameter | Impact | Range | Default |
|-----------|--------|-------|---------|
| atr_daily_bars | Smoother ATR, less noise | 5-50 | 15 |
| volume_avg_bars | Spike sensitivity | 3-10 | 5 |
| trend_bars | Trend detection speed | 3-10 | 5 |
| spike_threshold | Signal frequency | 1.0-5.0 | 2.0 |

---

## ⚠️ CRITICAL NOTES

1. **Always validate** - Don't allow invalid ranges
2. **Backward compatible** - Old config still works
3. **Hot reload** - No restart needed for config changes
4. **Database logging** - Log all config changes in bot_settings
5. **Alerts** - Notify user when config is invalid

---

## 📝 IMPLEMENTATION CHECKLIST

- [ ] Step 1: Add config parameters to trading_v3_artem.json
- [ ] Step 2: Implement _load_websocket_config() method
- [ ] Step 3: Replace all 5 hardcoded values (one by one!)
- [ ] Step 4: Add validation method (_validate_config)
- [ ] Step 5: Add hot reload call in _check_signal
- [ ] Step 6: Add Control Bot settings buttons
- [ ] Step 7: Test default behavior (should be identical)
- [ ] Step 8: Test each parameter independently
- [ ] Step 9: Test hot reload (config change without restart)
- [ ] Step 10: Commit to GitHub with detailed message

---

## 🔒 ROLLBACK PLAN

If something breaks:
```bash
# Revert to previous version
git revert <commit-hash>

# Or manually restore original config
git checkout HEAD -- config/trading_v3_artem.json
```

---

## 📊 TIMELINE

- Implementation: 60-90 minutes
- Testing: 30-45 minutes
- Total: 2-3 hours

---

**Status: READY FOR IMPLEMENTATION** ✅

When Artem approves, I will:
1. Implement all changes in order
2. Test thoroughly (default behavior unchanged)
3. Commit to GitHub
4. Verify Control Bot buttons work
5. Provide detailed documentation

No rushing, no breaking changes, maximum safety! 🛡️
