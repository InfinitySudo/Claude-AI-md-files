# 🎯 ПОЛНАЯ СТРУКТУРА ПРОЕКТА 4BotsBybit

## 📊 СТАТУС: PRODUCTION READY (v3)

---

## 🤖 БОТЫ И ПРОЦЕССЫ

### 1️⃣ **Control Bot** (ГЛАВНЫЙ)
```
Файл: src/control_bot_simple_v3.py
Запуск: systemd сервис /etc/systemd/system/bybit-control-bot.service
Функция: Управление всеми ботами через Telegram
Параметры: 
  - Запускает Signal Bot с паузой 35 сек
  - Запускает Trading Bot с паузой 20 сек после Signal
  - Запускает Strategy Switcher с паузой 10 сек после Trading
  - Health monitoring каждые 30 сек
  - Git управление (pull latest code)
```

### 2️⃣ **Signal Bot** (ОБНАРУЖЕНИЕ СИГНАЛОВ)
```
Файл: src/telegram_bot_runner_v3.py
Запуск: Control Bot запускает через subprocess
Зависимость: src/signal_bot_v3_websocket.py
Функция:
  - WebSocket подключение к ByBit (финский VPN)
  - Мониторинг 301 торговой пары (USDT perpetuals)
  - VARIANT 3: ATR + Volume dual confirmation
  - Запись сигналов в БД: signals_queue
  - Отправка уведомлений в Telegram
Инициализация: 35 секунд (загрузка candles)
```

### 3️⃣ **Trading Bot** (УПРАВЛЕНИЕ ПОЗИЦИЯМИ)
```
Файл: src/main_bot_v3.py
Запуск: Control Bot запускает через subprocess
Зависимости:
  - src/trading_bot_bybit.py (REST API)
  - src/paper_trading_simulator_v3.py (PAPER mode)
  - src/risk_manager_v3.py (SL/TP management)
  - src/price_monitor_v3.py (Real-time prices)
Функция:
  - Читает signals_queue из БД
  - Проверяет PAPER/REAL режим
  - Создает позиции с рассчитанными SL/TP
  - Закрывает позиции по TP/SL
  - Логирует в: simulated_trades (PAPER) или real_trades (REAL)
Инициализация: 20 секунд (после Signal Bot)
```

### 4️⃣ **Strategy Switcher** (АВТОМАТИЧЕСКИЙ ВЫБОР СТРАТЕГИИ)
```
Файл: src/strategy_switcher_v3.py
Запуск: Control Bot запускает через subprocess
Функция:
  - Каждый час проверяет win rate за последний час
  - Переключает между CONSERVATIVE (3 TP levels) и TREND (2 TP levels)
  - Логирует выбор в таблицу strategy_log
Инициализация: 10 секунд (после Trading Bot)
```

---

## 💾 БД (PostgreSQL)

```
Database: trading_bot_v3
Host: 127.0.0.1
Port: 5432
User: trading_bot
Password: trading_bot_password_123

ТАБЛИЦЫ (22 всего):
- signals_queue           ← Signal Bot пишет ТУТ
- simulated_trades        ← Trading Bot (PAPER mode)
- real_trades             ← Trading Bot (REAL mode)
- accepted_signals        ← История обработанных сигналов
- strategy_log            ← История переключений стратегий
- strategy_statistics     ← Статистика win rate
- tp_closures             ← История закрытий по TP
- websocket_prices        ← Текущие цены от WebSocket
- bot_state               ← Состояние системы
- bot_settings            ← Настройки ботов
- error_log               ← Логи ошибок
- sessions                ← Сессии Control Bot
+ другие вспомогательные таблицы
```

---

## 📁 ФАЙЛОВАЯ СТРУКТУРА

```
/root/.openclaw/workspace/projects/4BotsBybit/

├── src/                           # ОСНОВНОЙ КОД
│   ├── signal_bot_v3_websocket.py      # WebSocket для Signal Bot
│   ├── telegram_bot_runner_v3.py       # Signal Bot (main)
│   ├── main_bot_v3.py                  # Trading Bot (main)
│   ├── trading_bot_bybit.py            # Bybit REST API обертка
│   ├── strategy_switcher_v3.py         # Strategy Switcher
│   ├── control_bot_simple_v3.py        # Control Bot (main)
│   ├── paper_trading_simulator_v3.py   # PAPER mode engine
│   ├── risk_manager_v3.py              # SL/TP management
│   ├── price_monitor_v3.py             # Price monitoring
│   ├── notification_manager.py         # Telegram notifications
│   ├── hourly_reporter.py              # Hourly stats report
│   ├── telegram_client.py              # Telegram API wrapper
│   ├── logger.py                       # Logging system
│   └── ... (30+ других файлов v3)
│
├── config/                        # КОНФИГУРАЦИЯ
│   ├── symbols.json               # 301 торговые пары
│   ├── trading_v3_artem.json      # Параметры TP/SL
│   ├── settings.json              # Общие настройки
│   └── excluded_symbols.json      # Исключенные пары
│
├── start_bots_fixed.sh            # СКРИПТ ЗАПУСКА (с защитой)
├── start_bots_safe.sh             # Альтернативный запуск
│
├── logs/                          # ЛОГИ (НЕ ВКЛЮЧАТЬ В GIT)
│   ├── signal_bot_v3.log
│   ├── trading_bot_v3.log
│   ├── control_bot_v3.log
│   └── strategy_switcher_v3.log
│
├── versions/                      # BACKUP ВЕРСИЙ
│   ├── v3_production_31-03-2026_VARIANT3_READY/
│   ├── v1_stable_31-03-2026/
│   └── v2_variant3_broken_31-03-2026/
│
├── venv/                          # VIRTUAL ENV (НЕ ВКЛЮЧАТЬ)
└── .git/                          # GIT РЕПО

```

---

## 🔌 ПОДКЛЮЧЕНИЯ И ИНТЕГРАЦИИ

### ByBit API (с VPN туннелем)
```
REST API: api.bybit.com
WebSocket: stream.bybit.com
VPN: 46.8.232.182 (финский)
  - Туннельно ТОЛЬКО для ByBit
  - Telegram БЕЗ VPN
  - Другой интернет БЕЗ VPN

API Keys (в start_bots_fixed.sh):
  - BYBIT_API_KEY = Htba1UOPeL8ttQ9IRE
  - BYBIT_API_SECRET = gamytu41hfLOUZGRA7JWViudVMAG5DJXVKpr
```

### Telegram
```
Token: (в .env файле)
Chat ID: (используется для уведомлений)
Интерфейс: /status, /start, /stop, /restart, /update_code, /settings
```

### PostgreSQL
```
Host: 127.0.0.1
Port: 5432
Database: trading_bot_v3
User: trading_bot
Password: trading_bot_password_123
```

---

## 🚀 СКРИПТЫ ЗАПУСКА

### start_bots_fixed.sh (ОСНОВНОЙ)
```bash
# Запуск с автоматическими паузами и проверками:
1. Проверка дублей (предотвращение повторных запусков)
2. Signal Bot (35 сек инициализации)
3. Trading Bot (20 сек задержка)
4. Strategy Switcher (10 сек задержка)
5. Control Bot (через systemd - уже запущен)

Паузы:
- Signal Bot     35 сек (WebSocket + candles)
- Trading Bot    20 сек (DB init + modules)
- Strategy Sw    10 сек (setup)
```

---

## 📋 SYSTEMD СЕРВИСЫ

### /etc/systemd/system/bybit-control-bot.service
```ini
[Unit]
Description=ByBit Control Bot - Original Complete V3
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/projects/4BotsBybit
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/projects/4BotsBybit/src/control_bot_simple_v3.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## ✅ ИНВЕНТАРИЗАЦИЯ

### Запущенные процессы (сейчас):
```
1. Control Bot (systemd)         - ВСЕГДА ЖИВОЙ
2. Signal Bot (telegram_bot)     - Запускается Control Bot'ом
3. Trading Bot (main_bot_v3)     - Запускается Control Bot'ом
4. Strategy Switcher             - Запускается Control Bot'ом
```

### Версионирование:
- ✅ **Все файлы v3** (signal_bot_v3, main_bot_v3, control_bot_v3, etc.)
- ✅ **VARIANT 3**: ATR + Volume dual confirmation активна
- ✅ **Production ready**: Commit 5307272

---

## 📦 ПОДГОТОВКА К ПЕРЕНОСУ

### ДА (ВКЛЮЧИТЬ В GIT):
- ✅ src/ (все .py файлы v3)
- ✅ config/ (symbols.json, trading_v3_artem.json, settings.json)
- ✅ start_bots_fixed.sh
- ✅ start_bots_safe.sh
- ✅ /etc/systemd/system/bybit-control-bot.service
- ✅ DATABASE SCHEMA (sql backup)
- ✅ README.md (инструкции запуска)

### НЕТ (ИСКЛЮЧИТЬ):
- ❌ logs/ (runtime logs)
- ❌ venv/ (virtual environment)
- ❌ .env с credentials (использовать переменные окружения)
- ❌ versions/ (backup, но можно сохранить отдельно)

---

## 🎯 СТАТУС: READY FOR GITHUB TRANSFER

Всё готово к переносу на GitHub:
- Все компоненты идентифицированы
- Все зависимости задокументированы
- Все паузы и timing указаны
- Все БД таблицы перечислены
- Все файлы находятся в git

**Следующий шаг: Собрать в git репо и переместить на GitHub Artema**

