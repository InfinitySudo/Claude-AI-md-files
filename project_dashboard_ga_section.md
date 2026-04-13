---
name: Trading Dashboard — GA Section + Strategy Filters
description: Dashboard features added 2026-04-12: GA optimization UI, strategy wins highlight with status chips, max_drawdown setting
type: project
originSessionId: 4bf9c010-6bf6-4410-b91f-d3731633751f
---
## Dashboard изменения (2026-04-12)

**Performance by Strategy таблица:**
- Добавлена колонка "Wins" (кликабельная ссылка)
- Клик → подсвечивает выигрышные сделки в All Trades (не фильтрует)
- Status sort chips: TP / BE*TP / SL*TP / BE / SL / MANUAL
- Каждая категория с уникальным цветом фона + бордером + иконкой
- Цвета Win%: >0 = green, 0 = neutral (не red)

**SETTINGS_REGISTRY:**
- Добавлен `max_drawdown_percent` (trading_json, risk_management.max_drawdown_percent)

**GA Optimization секция в Settings tab:**
- Run / View Results / Apply / Rollback кнопки
- Weekly auto-run toggle
- Confirm phrases: "APPLY GA", "ROLLBACK GA"

**Nginx gotcha:** Dashboard HTML деплоится в `/var/www/dashboard/index.html` (НЕ /var/www/html/)

**Why:** Артём хотел видеть выигрышные сделки визуально + управлять GA из дашборда.
**How to apply:** cp TRADING_DASHBOARD.html /var/www/dashboard/index.html + restart dashboard-api
