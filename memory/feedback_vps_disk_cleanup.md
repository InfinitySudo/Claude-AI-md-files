---
name: vps-disk-cleanup-pattern
description: "Hostinger VPS 200GB. Главные мусорщики: /var/log/syslog (растёт без ротации), /root/.cache/pip, /var/crash, ontime backups. 2026-05-16 освободили 32 GB."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

## Где сидит мусор (по audit 2026-05-16)

| Path | Сколько было | Что | Безопасно ли чистить |
|---|---|---|---|
| `/var/log/syslog` + `syslog.1..N` | ~27 GB | rsyslog без агрессивной ротации | ✅ truncate + remove .gz |
| `/root/.cache/pip` | ~4 GB | pip download cache | ✅ `pip cache purge` |
| `/var/crash/*` | ~1.1 GB | crash reports | ✅ rm |
| `/var/log/journal/` | ~1 GB | systemd journal | ✅ `journalctl --vacuum-size=200M` |
| `/root/ontime/backend/backups/*.db.gz` | ~6.6 GB | daily backups, growing | ✅ keep last 14, delete older |
| `/root/4BotsBybit-Trading/data/klines/` | **53 GB** | 19,270 JSON files historical klines | ❌ **активно читаются** GA/backtester (atime check показал 19,270/19,270 в last 7d) |
| `/root/.cache/whisper` | 1.8 GB | Whisper models | ⚠ нужны voice-tutor'у |
| `/root/.cache/ms-playwright` | 1.3 GB | Playwright browsers | ⚠ для invoice OCR |

## One-liner для безопасной чистки (~38 GB)

```bash
# 1. truncate syslog
truncate -s 0 /var/log/syslog
rm -f /var/log/syslog.1 /var/log/syslog.2 /var/log/syslog.*.gz
# 2. journal
journalctl --vacuum-size=200M
# 3. pip cache
pip cache purge
# 4. crash dumps
rm -rf /var/crash/*
# 5. old ontime backups (keep 14)
cd /root/ontime/backend/backups
ls -1t *.db.gz | tail -n +15 | xargs -r rm
```

## Klines (53 GB) — НЕ удалять

`/root/4BotsBybit-Trading/data/klines/binance_*USDT_*.json` и `bybit_*USDT_*.json`. Все 19,270 файлов читаются за последние 7 дней — это работающий GA backtester. На PC2 (Tkach@100.99.211.123:`C:\Users\tkach\ga_gpu\klines`) есть только **partial copy** (532 файла, 1.22 GB) — не резерв.

**Альтернатива при необходимости освобождения**: gzip-сжать все JSON (текст хорошо жмётся ~5-7×, 53 GB → ~8-10 GB), адаптировать loader на `gzip.open`. Не делалось — пока 87 GB свободно.

## Долгосрочный фикс — logrotate для syslog

```bash
cat > /etc/logrotate.d/syslog-tight <<'EOF'
/var/log/syslog
{
    rotate 3
    daily
    missingok
    notifempty
    delaycompress
    compress
    size 500M
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
EOF
```

НЕ применялось — пока syslog снова не разрастётся (ориентировочно через 2-3 месяца).

## Disk state 2026-05-16 после cleanup

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1       193G  107G   87G  56% /
```

Раньше было 139G / 55G / 72%.

## Связано

- [[project-ga-optimizer]] — uses klines for backtest
- [[project-trading-bot-spec]] — main trading project (heaviest dir)
