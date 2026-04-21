---
name: OnTime wage-to-cost burden table
description: В OnTime `hourly_wage` (roster) — что получает работник; для бюджета и team-activity labour используется loaded cost через `_wage_to_cost(wage)`
type: project
originSessionId: f1c65322-19fe-4461-86eb-62acb1eaf226
---
OnTime финансовые расчёты используют два понятия ставки:

- `roster.hourly_wage` / `wage_history.hourly_wage` — то, что работник получает на руки. Видит его сам в team-activity (`wage` поле в API).
- **Loaded cost** — что компания платит за его час (wage + CPP/EI/WCB/vacation и т.д.). Вычисляется функцией `_wage_to_cost(wage)` в `ontime/backend/main.py` (рядом с `STATUSES`, ~line 100).

**Таблица** (точки, интерполяция линейная между соседями, extrapolate за пределами):

```
20 → 24.21   30 → 36.20   40 → 47.72
22 → 26.63   31 → 37.38   41 → 48.85
23 → 27.84   31.5 → 37.97 42 → 49.98
24 → 29.05   32 → 38.55   43 → 51.11
25 → 30.26   33 → 39.71   44 → 52.23
26 → 31.47   34 → 40.87   45 → 53.36
27 → 32.68   35 → 42.06   46 → 54.49
28 → 33.89   36 → 43.21
29 → 35.09   37 → 44.33
             38 → 45.46   38.5 → 46.03   39 → 46.59
```

Sanity: Aleksandr Taranenko, wage $30/h → loaded cost $36.20/h.

**Применяется в:**
- `enrich_project.spent_usd` (sessions + reports) — `main.py:~1421, ~1445`
- `project_budget` (`/api/projects/{pid}/budget`) — `spent_labour` через `_wage_to_cost`
- `project_team_history` (`/api/projects/{pid}/team-history`) — `labour_cost = total_hours × cost_rate`; response содержит и `wage`, и `cost_rate`
- `_calc_crew_budget` — `max_crew_hours = budget / avg(cost_rate)`, т.к. budget ограничен контрактом, а платим мы cost

**Why:** Artem's accounting sheet показывает реальные затраты на работника с burden. Budget/forecast должны отражать cost, не wage, иначе прибыль переоценивается.

**How to apply:** Если нужно добавить новый $-расчёт трудозатрат — всегда использовать `_wage_to_cost(wage)`, не raw `hourly_wage`. Если менялся burden (новые ставки CPP и т.д.) — обновлять `_WAGE_COST_TABLE` в одном месте.
