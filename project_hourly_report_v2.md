---
name: Hourly Report v2 (TG → dashboard deep-link)
description: Сжатый layout TG-отчёта + clickable close-reasons → дашборд с фильтром
type: project
originSessionId: 28e4b48c-7bcd-4db4-aef5-c902d730ffb0
---
С 2026-05-03 hourly TG-отчёт (`src/hourly_reporter.py`) переписан в два layout'а:

**Variant B (default)** — ~13 строк, 3 блока:
- `📡 PIPELINE`: одна строка `signals → accepted → trades · open · closed`
- `💰 RESULT`: WR, Net (gross/fees inline), Avg, по строке на стратегию `CONS N: TP1 X · SL Y`
- `🛡️ GUARDS`: verdict line + только TRIPPED-gates (ok-rows скрыты)
- Best/Worst/PF — только когда `closed >= 10`
- Other-pool block — только когда у второго пула есть activity

**Variant C** — auto-trigger когда `closed_count == 0 AND open_n == 0`, ~9 строк (только PIPELINE + GUARDS).

**Clickable close-reasons**: каждый counter в RESULT — HTML-ссылка на дашборд:
`<a href=".../?period=1h&close=SL&strategy=CONSERVATIVE#all-trades">SL 1 (50%)</a>`

**Dashboard deep-link contract** (`/var/www/dashboard/index.html` + `real.html`, плюс репо-копии):
- `?period=1h|24h|7d|...` → клик по `.period-btn[data-period=X]`
- `?close=SL|TP1|TP2|TP3|TP4|TP5|BE` + `?strategy=CONSERVATIVE|TREND|AGGRESSIVE` → JS заменяет `allTradesData` на отфильтрованную копию, перерисовывает `#all-trades-body`, рисует жёлтый баннер `🔗 Filtered from TG report` с кнопкой `clear`
- Якоря: `#tp-breakdown` (Take Profit Hit Rates), `#all-trades` (All Trades wrapper), `#guards` (только real.html, перед trading-state-banner)
- Loose match: `close=TP1` ловит и `TP1`, и `TP1(c)`, и `TP1*` в колонке Status

**Inline keyboard под отчётом** (3 кнопки): Main pool, Other pool, Guards & scorecard. URL-base — `os.getenv('DASHBOARD_URL', 'http://187.77.148.44:8080')`.

**How to apply**: при правке отчёта/дашборда — менять оба согласованно (params <-> JS handler). Если добавляешь новый close-reason код — добавь его в `_render_closes` и в JS-фильтр (loose match уже covers `XXX(c|t|a)*`).
