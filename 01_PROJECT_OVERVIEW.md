# 🤖 4BotsBybit - Advanced Bybit Trading Bot

**Real-time signal detection with WebSocket, risk management, and automated trading on Bybit exchange.**

---

## 📊 Overview

4BotsBybit is a comprehensive trading bot system consisting of:

- **Signal Bot V3** - WebSocket real-time signal detection with VARIANT 3 (ATR + Volume confirmation)
- **Trading Bot** - Position management, SL/TP calculation, risk control
- **Strategy Switcher** - Automatic strategy selection (CONSERVATIVE / TREND)
- **Control Bot** - Telegram management interface, health monitoring, code versioning
- **Hourly Reporter** - Statistics and performance tracking

---

## 🎯 Features

### Signal Detection (VARIANT 3)
```
✅ Real-time WebSocket kline monitoring (301 trading pairs)
✅ Volume spike detection (2.0x threshold)
✅ ATR-based trend confirmation
✅ Buy/Sell volume ratio analysis (1.0x threshold)
✅ Dual confirmation: ATR direction + Volume direction must match
```

### Trading Management
```
✅ PAPER mode (simulated trading for testing)
✅ REAL mode (live trading with risk management)
✅ Dual TP levels (CONSERVATIVE: 3 levels, TREND: 2 levels)
✅ Dynamic SL calculation based on ATR
✅ Risk per trade control (default $0.10)
```

### Control Interface
```
✅ Telegram bot management
✅ Real-time system status
✅ Code version tracking (git integration)
✅ Parameter tuning (volume, spike, B/S ratio)
✅ Health monitoring with auto-alerts
```

---

## 📁 Project Structure

```
4BotsBybit/
├── src/
│   ├── signal_bot_v3_websocket.py      # Real-time signal detection
│   ├── trading_bot_bybit.py            # Trading logic & SL/TP
│   ├── telegram_bot_runner_v3.py       # Signal -> Telegram formatter
│   ├── control_bot_simple_v3.py        # Management interface
│   ├── strategy_switcher_v3.py         # Strategy selection
│   ├── bybit_api.py                    # REST API wrapper
│   ├── bybit_websocket.py              # WebSocket client
│   ├── logger.py                       # Logging system
│   ├── paper_trading_simulator_v3.py   # PAPER mode engine
│   ├── notification_manager.py         # Alert system
│   ├── hourly_reporter.py              # Statistics
│   └── telegram_client.py              # Telegram API wrapper
│
├── config/
│   ├── symbols.json                    # 301 trading pairs
│   └── wg0.conf                        # VPN configuration
│
├── logs/
│   ├── signal_bot_v3.log              # Signal Bot logs
│   ├── trading_bot_v3.log             # Trading Bot logs
│   ├── control_bot_v3.log             # Control Bot logs
│   └── strategy_switcher_v3.log       # Strategy logs
│
├── versions/
│   └── v3_production_*/               # Code backups
│
├── venv/                              # Python virtual environment
├── .git/                              # Git repository
├── .gitignore                         # Git exclusions
├── README.md                          # This file
└── CONTRIBUTING.md                    # Development guide

```

---

## 🚀 Quick Start

### Requirements
```
Python 3.9+
PostgreSQL 12+
Bybit API keys (for trading)
Telegram bot token
```

### Setup

```bash
# 1. Clone repository
git clone https://github.com/InfinitySudo/4BotsBybit.git
cd 4BotsBybit

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
# - Set Bybit API keys in src/
# - Configure PostgreSQL connection
# - Get Telegram bot token

# 5. Start system
systemctl start bybit-control-bot.service
```

### Management

```bash
# Via Telegram Control Panel:
Settings → 📊 Status          # System status
Settings → 🟢 Start           # Start all bots
Settings → 🛑 Stop            # Stop all bots
Settings → 🔄 Restart         # Restart all bots
Settings → 📦 Update Code     # Pull latest code from GitHub
Settings → 🔍 Signal Bot Parameters  # Tune thresholds
```

---

## ⚙️ Configuration

### Signal Bot Parameters

```
Volume Threshold: $100,000 (minimum volume for signal)
Spike Ratio: 2.0x (minimum spike multiplier)
B/S Threshold: 1.0x (buy/sell volume ratio requirement)
```

### Trading Parameters

```
Risk per Trade: $0.10 (default)
CONSERVATIVE TP: 3 levels (2%, 4%, 6%)
TREND TP: 2 levels (3%, 6%)
Leverage: 5x (customizable)
```

---

## 📊 Monitoring

### Real-time Metrics
```
✅ Signal detection rate (signals/hour)
✅ Win rate (% profitable trades)
✅ Total P&L (profit/loss)
✅ Active positions (count)
✅ System health (CPU, memory, connections)
```

### Hourly Reports
Automatic Telegram reports every hour with:
- Signals detected
- Trades created
- Win rate
- P&L
- System health status

---

## 🔒 Security

```
✅ VPN-only API connections (Bybit)
✅ Local PostgreSQL (no remote exposure)
✅ Token-based GitHub access
✅ Encrypted credentials in environment
✅ Systemd service isolation
```

---

## 📝 Development

See `CONTRIBUTING.md` for:
- Git workflow
- Commit conventions
- Testing requirements
- Code review process

---

## 🐛 Troubleshooting

### Signals not generating
```
Check: Volume > $100k ✅
Check: Spike > 2.0x ✅
Check: B/S ratio clear (> 1.0x) ✅
Check: ATR + Volume both confirm direction ✅
```

### Position not created from signal
```
Check: Risk mode (PAPER vs REAL) ✅
Check: Leverage sufficient ✅
Check: Margin available ✅
Check: Trading hours (if restricted) ✅
```

### Code not updating
```
git fetch origin develop
git pull origin develop
systemctl restart bybit-control-bot.service
```

---

## 📞 Support

Issues? Check the logs:
```
tail -100 logs/signal_bot_v3.log
tail -100 logs/trading_bot_v3.log
tail -100 logs/control_bot_v3.log
```

---

## 📄 License

Proprietary - InfinitySudo

---

**Last Updated:** 2026-04-02  
**Current Version:** v3 Production  
**Commit:** 57ddf5d
