# 📊 4BotsBybit - ПОЛНЫЙ АНАЛИЗ ПРОЕКТА (Сессия 1)

**Дата:** 08 апреля 2026  
**Версия:** v3 Production  
**Статус:** Ready for Analysis & Development  
**Автор:** Artem Borysiuk  

---

## 🎯 ЦЕЛЬ ПРОЕКТА

Полностью автоматизированный торговый бот для Bybit с использованием:
- 🎯 WebSocket real-time сигналов (VARIANT 3 - Dual Confirmation)
- 💰 Умного риск-менеджмента ($0.10 фиксированный риск)
- 🔄 Автоматического переключения стратегий (по win_rate)
- 📱 Telegram control panel для live управления
- 🎭 Paper Trading для безопасного тестирования

---

## 🤖 АРХИТЕКТУРА СИСТЕМЫ (4-УРОВНЕВАЯ)

### **Уровень 1: Control Bot (Главный Оркестратор)**
```
Файл: src/control_bot_simple_v3.py
Запуск: systemd сервис bybit-control-bot.service
Функции:
  ✅ Управление всеми ботами через Telegram
  ✅ Health monitoring каждые 30 сек
  ✅ Git версионирование (pull latest code)
  ✅ Параметры сигналов в реал-тайме
  ✅ Запуск/остановка компонентов
  ✅ Отправка статуса и алертов

Telegram команды:
  /status          → Статус всех компонентов
  /start           → Запуск всех ботов
  /stop            → Остановка всех ботов
  /settings        → Управление параметрами
  /update_code     → Git pull latest
```

### **Уровень 2: Signal Bot V3 (WebSocket Real-Time Detection)**
```
Файл: src/telegram_bot_runner_v3.py + src/signal_bot_v3_websocket.py
Запуск: Control Bot через subprocess (35 сек инициализации)
Функции:
  ✅ WebSocket подключение к ByBit (через VPN 46.8.232.182)
  ✅ Мониторинг 301 торговой пары (USDT perpetuals)
  ✅ VARIANT 3: Dual Confirmation (ATR + Volume)
  ✅ Запись сигналов в БД (signals_queue)
  ✅ Telegram notifications при новых сигналах

Инициализация: 35 сек (загрузка дневных свечей + ATR)
```

### **Уровень 3: Trading Bot V3 (Position Management)**
```
Файл: src/main_bot_v3.py + src/trading_bot_bybit.py
Запуск: Control Bot через subprocess (20 сек после Signal Bot)
Функции:
  ✅ Чтение сигналов из signals_queue
  ✅ Расчет SL/TP (Risk Manager)
  ✅ PAPER mode: симуляция без реальных ордеров
  ✅ REAL mode: выставляет реальные ордера
  ✅ Логирует в simulated_trades или real_trades
  ✅ Мониторинг открытых позиций

Инициализация: 20 сек (DB init + modules)
```

### **Уровень 4: Strategy Switcher V3 (Auto-Adaptation)**
```
Файл: src/strategy_switcher_v3.py
Запуск: Control Bot через subprocess (10 сек после Trading Bot)
Функции:
  ✅ Часовой мониторинг win_rate
  ✅ CONSERVATIVE (≤35% win) → 3 TP уровня
  ✅ TREND (>35% win) → 5 TP уровней
  ✅ Сохранение в strategy_log

Логика:
  - Каждый час пересчитывает win_rate
  - Если переключение нужно → обновляет конфиг
  - Новые сделки используют новую стратегию
```

---

## 🎯 СИГНАЛ-ГЕНЕРАЦИЯ (VARIANT 3 - DUAL CONFIRMATION)

### **Параметры (из trading_v3_artem.json):**
```json
{
  "volume_threshold_usd": 100000,
  "spike_ratio": 2.0,
  "bs_ratio": 1.0,
  "atr_daily_bars": 15,
  "volume_avg_bars": 5,
  "trend_bars": 5
}
```

### **Логика обнаружения:**

**Условие 1: Volume Spike**
```
Current Volume > Average Volume × 2.0
→ Обнаружен спайк объёма
```

**Условие 2: Buy/Sell Ratio**
```
BUY сигнал:  Buy Volume > Sell Volume × 1.0
SHORT сигнал: Sell Volume > Buy Volume × 1.0
```

**Условие 3: ATR Trend Confirmation (КРИТИЧНО!)**
```
Направление ATR должно совпадать с направлением B/S ratio
- Если B/S говорит BUY, но ATR падает → ОТКЛОНИТЬ сигнал
- Если B/S говорит BUY И ATR растет → ПРИНЯТЬ сигнал
```

**Результат:**
- ✅ Высокая точность (фильтрация ложных сигналов)
- ✅ Двойная проверка направления
- ✅ Cooldown 60 сек между сигналами

---

## 💰 ТРИ СТРАТЕГИИ ТОРГОВЛИ

### **Стратегия 1: CONSERVATIVE (Защитная)**
```
Условие:      Win Rate ≤ 35%
Размер позиции: 0.5x base ($0.05 риск)
TP Levels:    [1%, 3%, 5%]
Distribution: [50%, 30%, 20%]
SL:           ATR × 0.1 (защита вниз)
Назначение:   Защита капитала в неудачных периодах
```

**Пример:**
- Сигнал: BTCUSDT LONG
- Entry: $43,500
- SL: $43,450 (ATR-based)
- TP1: $43,935 (1%, 50% позиции)
- TP2: $44,805 (3%, 30% позиции)
- TP3: $45,675 (5%, 20% позиции)

### **Стратегия 2: TREND (Трендовая)**
```
Условие:      Win Rate 35-49%
Размер позиции: 1.0x base ($0.10 риск)
TP Levels:    [1.5%, 4%, 7%, 10%, 15%]
Distribution: [30%, 25%, 20%, 15%, 10%]
SL:           ATR × 0.1
Назначение:   Балансировка риска и прибыли
```

### **Стратегия 3: AGGRESSIVE (Агрессивная)**
```
Условие:      Win Rate ≥ 50%
Размер позиции: 2.0x base ($0.20 риск)
TP Levels:    [2%, 5%, 10%, 15%, 25%]
Distribution: [25%, 25%, 20%, 15%, 15%]
SL:           ATR × 0.1
Назначение:   Максимизация прибыли в успешные периоды
```

---

## 💾 БАЗА ДАННЫХ (PostgreSQL)

### **Подключение:**
```
Host: 127.0.0.1
Port: 5432
Database: trading_bot_v3
User: trading_bot
Password: trading_bot_password_123
Pool: 10 connections
Timeout: 10 сек
```

### **Главные таблицы:**

| Таблица | Назначение | Заполняет |
|---------|-----------|-----------|
| `signals_queue` | Входящие сигналы | Signal Bot |
| `accepted_signals` | Обработанные сигналы | Trading Bot |
| `simulated_trades` | PAPER mode сделки | Trading Bot |
| `real_trades` | REAL mode сделки | Trading Bot |
| `tp_closures` | TP выполнения | Trading Bot |
| `strategy_log` | Переключения стратегий | Strategy Switcher |
| `strategy_statistics` | Win rate, P&L | Trading Bot |
| `websocket_prices` | Real-time цены | Signal Bot |
| `bot_state` | Состояние ботов | Control Bot |
| `error_log` | Логи ошибок | Все боты |

### **IPC Синхронизация:**
```
Signal Bot → signals_queue → Trading Bot → simulated_trades/real_trades
                                            ↓
                              Strategy Switcher ← strategy_statistics
```

---

## 🔌 ИНТЕГРАЦИИ

### **1. ByBit API (через финский VPN)**
```
REST API Host: api.bybit.com:443
WebSocket Host: stream.bybit.com
VPN Tunnel: 46.8.232.182 (финский IP)
API Key: Htba1UOPeL8ttQ9IRE
API Secret: gamytu41hfLOUZGRA7JWViudVMAG5DJXVKpr
Mode: MAINNET (testnet: false)
```

### **2. Telegram Control & Reporting**
```
Control Bot Token: (в systemd env или config)
Signal Bot Token: (в config)
Reporting Bot Token: 8608873544:AAGXktUrdGHyrXnbNfpluHhVIWTTFSJYcyM
Report Chat ID: ${TELEGRAM_REPORT_CHAT_ID}

Интерфейс:
  - Telegram polling (не webhook)
  - Text input для параметров
  - Inline buttons для быстрых команд
```

### **3. PostgreSQL IPC**
```
Все 4 бота используют одну БД:
- Signal Bot: пишет в signals_queue
- Trading Bot: читает signals_queue, пишет в trades
- Strategy Switcher: пишет в strategy_log
- Control Bot: читает bot_state

Преимущества:
  ✅ Простая синхронизация
  ✅ Persistent state
  ✅ Легко дебагировать
  ✅ Нет network overhead
```

---

## 📁 ФАЙЛОВАЯ СТРУКТУРА

### **Размер проекта:**
```
Всего Python кода: 20,564 строк
Количество файлов: 50+ (v3 компоненты)
Главные модули: 15+ (signal, trading, strategy, control, etc.)
Config файлы: 5+ JSON файлов
```

### **Структура директорий:**
```
/root/4BotsBybit-Production/
├── src/
│   ├── 🎯 ОСНОВНЫЕ КОМПОНЕНТЫ
│   │   ├── control_bot_simple_v3.py         (707 строк)
│   │   ├── signal_bot_v3_websocket.py       (412 строк)
│   │   ├── telegram_bot_runner_v3.py        (301 строк)
│   │   ├── main_bot_v3.py                   (634 строк)
│   │   ├── strategy_switcher_v3.py          (402 строк)
│   │   
│   ├── 🔧 ByBit ИНТЕГРАЦИЯ
│   │   ├── bybit_api.py                     (REST API)
│   │   ├── bybit_websocket.py               (WebSocket)
│   │   ├── trading_bot_bybit.py             (Order executor)
│   │   
│   ├── 💰 RISK & POSITION MANAGEMENT
│   │   ├── risk_manager_v3.py               (SL/TP calc)
│   │   ├── paper_trading_simulator_v3.py    (PAPER mode)
│   │   ├── order_executor_v3.py             (Order placement)
│   │   ├── price_monitor_v3.py              (Real-time prices)
│   │   
│   ├── 📊 MONITORING & REPORTING
│   │   ├── hourly_reporter.py               (Stats every hour)
│   │   ├── daily_reporter.py                (Daily summary)
│   │   ├── statistics_manager_v3.py         (Win rate tracking)
│   │   ├── monitoring_control_v3.py         (Health checks)
│   │   
│   ├── 💾 DATABASE & UTILITIES
│   │   ├── database_v3.py                   (PostgreSQL connector)
│   │   ├── logger.py                        (Logging system)
│   │   ├── telegram_client.py               (Telegram API)
│   │   ├── notification_manager.py          (Alerts)
│   │   
│   └── ... (30+ других файлов)
│
├── config/
│   ├── trading_v3_artem.json                (Все параметры)
│   ├── symbols.json                         (301 торговая пара)
│   ├── settings.json                        (Общие настройки)
│   └── excluded_symbols.json                (Исключения)
│
├── logs/                                    (Runtime logs)
│   ├── signal_bot_v3.log
│   ├── trading_bot_v3.log
│   ├── control_bot_v3.log
│   └── strategy_switcher_v3.log
│
└── versions/                                (Backups)
    ├── v3_production_31-03-2026/
    └── v1_stable_31-03-2026/
```

---

## 🚀 ЗАПУСК И РАЗВЕРТЫВАНИЕ

### **systemd Service:**
```ini
[Unit]
Description=ByBit Control Bot - v3 Production
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/4BotsBybit-Production
ExecStart=/usr/bin/python3 /root/4BotsBybit-Production/src/control_bot_simple_v3.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### **Порядок запуска (с паузами):**
```
1. systemd запускает Control Bot
   ↓
2. Control Bot запускает Signal Bot (subprocess)
   ⏳ Pause 35 сек (WebSocket инициализация)
   ↓
3. Control Bot запускает Trading Bot (subprocess)
   ⏳ Pause 20 сек (DB инициализация)
   ↓
4. Control Bot запускает Strategy Switcher (subprocess)
   ⏳ Pause 10 сек (setup)
   ↓
5. Control Bot начинает health monitoring (каждые 30 сек)
```

### **Health Monitoring:**
```
Каждые 30 сек Control Bot проверяет:
  ✅ Signal Bot жив? (проверка процесса)
  ✅ Trading Bot жив? (проверка процесса)
  ✅ Strategy Switcher жив? (проверка процесса)
  ✅ PostgreSQL доступна? (test query)
  ✅ ByBit доступна? (API ping)
  ✅ Telegram доступна? (API ping)

Если компонент умер → restart его
```

---

## 💰 ФИНАНСОВЫЕ ПАРАМЕТРЫ

### **Базовые:**
```json
{
  "capital_usd": 100,
  "risk_per_trade_usd": 0.10,        // Фиксированный риск
  "min_order_size_usd": 10,
  "max_order_size_usd": 100,
  "min_balance_to_trade_usd": 50,
  "leverage": 35.0                    // Max, default 5x
}
```

### **Динамическое управление рисками:**
```
Base Position Size: $0.1

if win_rate ≤ 35%:
  → Position Size = $0.1 × 0.5 = $0.05 (CONSERVATIVE)

if 35% < win_rate < 50%:
  → Position Size = $0.1 × 1.0 = $0.10 (TREND)

if win_rate ≥ 50%:
  → Position Size = $0.1 × 2.0 = $0.20 (AGGRESSIVE)
```

### **Performance Targets:**
```
Daily Target:        +2.5%  ($2.50/день на $100)
Expected Win Rate:   55%
Expected Profit/Day: $2.50
Daily Max Loss:      -5%    ($5.00 стоп)

Примечание:
- При достижении -5% за день → Rest Mode (24 часа без торговли)
- Защита капитала ВАЖНЕЕ чем максимизация прибыли
```

### **Trading Schedule:**
```
US Summer (EDT): 13:30-20:00 UTC (6.5 часов)
US Winter (EST): 14:30-21:00 UTC (6.5 часов)
Weekend Trading: false
Holidays: 26 дней (все US holidays в 2026)
```

---

## 🔒 SECURITY & BEST PRACTICES

### **Безопасность:**
```
✅ VPN туннель ТОЛЬКО для ByBit (не для Telegram/интернета)
✅ PostgreSQL локальная на 127.0.0.1 (нет remote exposure)
✅ API ключи в config JSON (можно переместить в env vars)
✅ Telegram токены защищены
✅ systemd сервис запускается как root (необходимо для системы)
✅ Логи ротируются автоматически
✅ Graceful shutdown (отправляет алерт в Telegram перед выключением)
```

### **Resilience:**
```
✅ Автоматический restart при крахе компонента
✅ Retry механизм для API запросов
✅ Database connection pooling
✅ Backoff strategy для ошибок
✅ Health monitoring с alerts
```

---

## 📊 MONITORING & REPORTING

### **Real-Time Metrics:**
```
✅ Active positions count
✅ Current P&L (симулированный и реальный)
✅ Win rate (%)
✅ Signals detected (в час)
✅ System health (CPU, memory, connections)
✅ Last signal time
✅ Last trade time
```

### **Hourly Reports (автоматические):**
```
Отправляется в Telegram каждый час:
- Сигналов обнаружено: N
- Сделок создано: N
- Закрыто: N (X wins, Y losses)
- Win Rate: X%
- P&L за час: $X.XX
- Активные позиции: N
- Текущая стратегия: CONSERVATIVE/TREND/AGGRESSIVE
- System health: ✅ OK / ⚠️ WARNING / 🔴 CRITICAL
```

### **Daily Reports:**
```
Ежедневно в 21:00 UTC:
- Total P&L за день: $X.XX
- Win rate за день: X%
- Best trade: +$X.XX
- Worst trade: -$X.XX
- Hours traded: X
- Biggest drawdown: -$X.XX
- Current strategy: X
```

---

## ✅ КЛЮЧЕВЫЕ РЕШЕНИЯ & ПАТТЕРНЫ

### **1. VARIANT 3 (Dual Confirmation)**
**Проблема:** Много ложных сигналов от volume spike  
**Решение:** Требуем совпадения ATR direction + B/S ratio direction  
**Результат:** ↑ Точность сигналов, ↓ Ложные срабатывания  

### **2. Dynamic Strategy Switching**
**Проблема:** Один размер позиции не подходит для всех рыночных условий  
**Решение:** Меняем стратегию на основе win_rate (каждый час)  
**Результат:** Адаптация к рынку, защита в плохих условиях, прибыль в хороших  

### **3. Fixed Risk Approach**
**Проблема:** % от счета неопределен при убытках  
**Решение:** Фиксированный риск $0.10 на сделку  
**Результат:** Предсказуемая защита капитала, easy management  

### **4. Paper Trading Mode**
**Проблема:** Невозможно безопасно тестировать новые параметры  
**Решение:** Полная симуляция с реальными сигналами и ценами  
**Результат:** Можно менять параметры БЕЗ риска денег  

### **5. PostgreSQL IPC**
**Проблема:** 4 независимых процесса нужно синхронизировать  
**Решение:** Одна БД как central message bus  
**Результат:** Simple, reliable, debuggable  

---

## 🎯 CURRENT STATUS

- ✅ **v3 Production Ready** - все компоненты работают
- ✅ **Все интеграции** - ByBit, Telegram, PostgreSQL активны
- ✅ **Git версионирование** - code tracking включена
- ✅ **PAPER MODE** - тестирование без риска
- ✅ **Telegram контроль** - live управление с мобилки
- ✅ **301 пара** - мониторится в реал-тайме
- ✅ **Health monitoring** - автоматические рестарты
- ⏳ **REAL MODE** - готово, но нужна активация вручную

---

## 🚀 ЧТО ДАЛЬШЕ?

Возможные направления развития:

1. **Оптимизация VARIANT 3** - улучшить параметры сигналов
2. **Новые стратегии** - добавить 4-ю, 5-ю стратегию
3. **Backtesting** - анализ исторических данных
4. **Machine Learning** - обучить модель на данных
5. **Web Dashboard** - красивый frontend для мониторинга
6. **Multi-Account** - управление несколькими счетами Bybit
7. **Risk Optimization** - Kelly Criterion или другие формулы
8. **Production Deploy** - готовность к REAL MODE на реальные деньги

---

## 📚 ДОКУМЕНТАЦИЯ

Этот файл - **Session 1** основной анализ проекта. В дальнейшем будут добавляться:
- Session 2, 3, N... по мере нашей работы
- Все MD файлы сохраняются в Git
- Контекст всех обсуждений запоминается

---

**Статус:** ✅ ПОЛНОСТЬЮ ПРОАНАЛИЗИРОВАНО И ЗАДОКУМЕНТИРОВАНО
