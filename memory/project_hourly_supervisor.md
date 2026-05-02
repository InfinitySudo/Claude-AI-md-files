---
name: Hourly Supervisor (deterministic)
description: 2026-05-02 — старый opus/sonnet hourly agent заменён Python-скриптом; Claude (haiku) только при events>=1 или anomalies>=5; quiet час = 0 LLM calls
type: project
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
**Что:** `bybit-claude-hourly.service` теперь запускает `scripts/run_hourly_supervisor.sh` → `scripts/hourly_supervisor.py` (Python без Claude в hot path). Старый `run_hourly_claude.sh` + `claude_hourly_check.md` оставлены на диске для rollback.

**Why:** Старый supervisor — `claude -p` agent (sonnet/opus, multi-step, ~200 line prompt) сжигал 50-200 messages за прогон даже когда всё спокойно. При 5×/день (раньше) это давало рейт-лимит exhaustion на opus/sonnet, и интерактивный `claude-telegram-bot` упирался в «Лимит исчерпан». Реальная judgment работа была только при event'ах — остальное (drain queue, curl APIs, journalctl, форматирование) детерминированно и Claude для этого не нужен.

**How to apply:**
- Файл: `/root/4BotsBybit-Trading/scripts/hourly_supervisor.py`
- Делает: drain `claude_event_queue`, `_curl_json` snapshot (trader-stats / dd / scorecard / blacklist), DB peek (current_strategy + strategy_mode), `systemctl is-active` для известных units, `journalctl -p warning` за 1ч
- **Trigger Claude (haiku)**: `len(events) >= 1` ИЛИ `len(anomalies) >= 5`
- **Quiet hour**: pure Python, ~3 секунды, 0 API calls
- **Telegram отчёт** через `claude_notifier.send_telegram(text, severity)` — формат фиксированный (events / snapshot / guards / anomalies / triage), severity = info/warn/critical

**Tunables в скрипте:**
- `CLAUDE_TRIGGER_EVENTS = 1`
- `CLAUDE_TRIGGER_ANOMALIES = 5`
- `JOURNAL_HOURS = 1`
- `LOG_UNITS` (для journalctl) — bybit-signalbot, bybit-tradingbot, dashboard-api
- `SERVICES` — для systemctl is-active (skip non-existent units чтобы не false-trip critical)

**Расписание timer'ов 2026-05-02:**
- `bybit-claude-hourly.timer` — 2×/день: 06:00 и 18:00 Calgary
- `bybit-claude-watchdog.timer` — 4×/день: 06:00, 12:00, 18:00, 22:00 Calgary
- Раньше было 5+5 = 10 в сутки. Теперь 2+4 = 6.

**Если нужно откатить:** `systemctl edit bybit-claude-hourly.service` → ExecStart обратно на `run_hourly_claude.sh`.
