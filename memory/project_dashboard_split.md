---
name: Dashboard split into PAPER + REAL pages
description: Two URLs, two HTML files, source param on stats endpoints — explicit so paper/real numbers can never be confused
type: project
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
After hybrid mode (per_strategy paper/real routing), one dashboard
mixing both pools made every number ambiguous. Split into two pages
2026-04-23.

## URLs

- `/` (or `/index.html`) → 📒 **PAPER** view — yellow nav highlight.
  - Source of data: `simulated_trades`.
  - Default landing.
- `/real.html` → 💰 **REAL** view — green nav highlight + red
  "REAL MONEY" warning.
  - Source: `real_trades`.

Top nav present on both, switches between them with one click. Hint
at right edge: "Hybrid mode: CONS→paper, TREND/AGGR→real".

## Backend (`src/dashboard_api_v3.py`)

Three endpoints accept `?source=paper|real` (default `paper`):
- `/api/trader-stats` — main stats endpoint, summary + per-strategy
  blocks + open positions + recent/all trades + tp_hits + pnl_history
  all parameterized on the resolved table.
- `/api/funnel-history`
- `/api/symbol-breakdown`

Response envelope and `summary` block include `source` and `mode`
reflecting the requested view (not the bot's global flag).

## Frontend wiring

- `window.DASHBOARD_SOURCE = 'real'` set on `real.html`; default
  `'paper'` on index.
- All `fetch()` URLs append `&source=${DASHBOARD_SOURCE}`.
- Hero title and `<title>` differentiate so an open tab is always
  recognizable at a glance.

## Repo mirrors

`/var/www` is unversioned (see `project_unversioned_prod_state`). Repo
copies are the canonical source:
- `TRADING_DASHBOARD.html` → mirror of `/var/www/dashboard/index.html`
  (paper)
- `TRADING_DASHBOARD_REAL.html` → mirror of `/var/www/dashboard/real.html`
  (real)

After editing repo copies, `cp` them into `/var/www/dashboard/`.
After live-editing `/var/www/dashboard/`, mirror back to repo before
commit.

**Why:** Money is involved — operators can't afford to misread which
pool's numbers are on screen.

**How to apply:** Any new stats endpoint must take `?source` param.
Any new dashboard widget must derive its data via the
`DASHBOARD_SOURCE` constant, not hardcode `simulated_trades` or
`real_trades` in JS.
