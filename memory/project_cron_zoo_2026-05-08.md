---
name: Trading bot cron-зоопарк 2026-05-08
description: Все 10 systemd timer'ов trading-системы после rebuild сессии 2026-05-08 — что запускается, когда, зачем
type: project
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
Все таймеры локальное время Calgary (America/Edmonton, OnCalendar default = local per `feedback_systemd_oncalendar_local_time`).

| Timer | Cadence | Скрипт/Юнит | Назначение |
|---|---|---|---|
| `bybit-risk-officer.timer` | hourly | `scripts/risk_officer.py` | LLM defensive auto-pause (см. `project_risk_officer`) |
| `bybit-claude-watchdog.timer` | 06,12,18,22 | `src/claude_watchdog.py` | Critical event detector (старая infra) |
| `bybit-claude-hourly.timer` | 06, 18 | `scripts/run_hourly_supervisor.sh` | Hourly supervisor (детерминистический, haiku только on events) |
| `bybit-divergence-monitor.timer` | every 4h | divergence script | Real vs paper |
| `bybit-daily-summary.timer` | **06:30** | `scripts/daily_summary.py` | TG digest утром (wallet, trades, RO, ML) |
| `bybit-anomaly-detector.timer` | **06:00** | `scripts/anomaly_detector.py` | Stale/high-fee/divergence/orphans → TG warn |
| `bybit-auto-blacklist.timer` | **03:00** | `scripts/auto_blacklist.py` | Удаляет токсичные монеты (≥5t / WR<30% / net<−$1 / 7d) |
| `bybit-db-backup.timer` | **02:00** | `scripts/db_backup.py` | pg_dump → scp ПК1, retention 30d |
| `bybit-meta-retrain.timer` | **Sun 04:00** | `scripts/ml/weekly_retrain.sh` | Meta-labeler retrain на ПК1, deploy если AUC ≥ old + 0.01 |
| `bybit-ga-weekly.timer` | Sun 17:00 | `scripts/ga_weekly_run.sh` | Полный GA |

**Order matters утром:**
1. 02:00 DB backup (выйти до auto-blacklist)
2. 03:00 Auto-blacklist (выйти до anomaly + summary)
3. 06:00 Anomaly detector
4. 06:30 Daily summary (захватывает свежий blacklist + anomaly state)

**Что НЕ trigger'ится автоматически:**
- GA full run (требует `/api/ga/run target=pc1` через dashboard)
- Risk Officer LLM (включается только в CAUTION zone, и сейчас вообще OFF на 7 дней)
- TG slash commands (push-driven, см. project_baseline_v2)

**Если timer молчит дольше cadence:**
1. `systemctl status <name>.service` — последний exit
2. `journalctl -u <name>.service --since '1 day ago'`
3. Если PostgreSQL down → все DB-зависимые timer'ы упадут
4. Если ПК1 down (Tailscale) → ga-weekly + meta-retrain + db-backup пострадают, но другие OK
