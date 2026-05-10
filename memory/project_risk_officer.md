---
name: Risk Officer — hourly LLM defensive auto-pause
description: Активен 2026-05-08, hybrid scorecard+LLM gate, может только pause/resume через /api/trading-state; LLM-on-CAUTION временно OFF на 7 дней
type: project
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
**Что:** Каждый час `bybit-risk-officer.timer` запускает `scripts/risk_officer.py`. Снапшот живого state → деттерминированный решатель → если CAUTION zone, escalate to Claude haiku ($0.10 cap). Может ТОЛЬКО pause/resume через `/api/trading-state`. Не модифицирует параметры/позиции/leverage.

**Decision tree:**
- verdict=GO → silent observe
- verdict=STOP + auto_pause_on_stop=true → pause (no LLM, free)
- verdict=CAUTION + LLM enabled → claude haiku → JSON {action,duration,reason}
- already paused by operator → never override

**Safety rails:**
- Cooldown 1h между flips
- Daily flip cap 4
- Daily LLM call cap 30
- Officer pauses tagged `risk_officer:` — резюмит ТОЛЬКО свои pause'ы
- Любая ошибка → OBSERVE (no action)

**Settings (bot_settings table):**
- `risk_officer_enabled=true`
- `risk_officer_auto_pause_on_stop=true`
- `risk_officer_use_llm_on_caution=FALSE` (временно с 2026-05-08 на 7 дней — мало данных, LLM срабатывал часто на «Missing WR data»)
- `risk_officer_max_pause_hours=8`
- `risk_officer_llm_model=haiku`

**State tracking:** `risk_officer_active_pause` (bot_settings bool) ставится в true при officer-pause, чистится на resume. `bot_settings.risk_officer_last_pause_at` timestamp.

**Audit:** `risk_officer_decisions` table (snapshot JSONB, verdict, action, reason, applied, error, created_at). Endpoint `/api/risk-officer/status` отдаёт last 10 decisions + 24h stats для dashboard widget.

**Снапшот источники (bundled HTTP calls):**
- `/api/scorecard?source=real` — verdict + fail_count
- `/api/real-snapshot` — open + realized 1h/24h/7d
- `/api/dd/status` — daily/weekly DD
- `/api/trader-stats?period=1h&source=real` — per-strategy SL streak
- `/api/trading-state` — current state
- Bybit `/v5/market/tickers?symbol=BTCUSDT` — BTC 24h move + funding rate

**TG alerts (через `claude_notifier.send_telegram`):** PAUSE → 🚨 alert; RESUME → ⚠️ warn; LLM-OBSERVE → 🤖 info; verdict=GO → silent.

**Re-enable LLM-on-CAUTION после ~50+ post-baseline сделок** (когда verdict стабилизируется и больше не CAUTION-by-default из-за sparse data). Команда:
```
curl -X POST http://127.0.0.1:8000/api/settings/risk_officer_use_llm_on_caution -d '{"value":"true"}'
```
