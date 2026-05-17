---
name: dashboard-v2-deploy-script
description: "nginx сервит из /var/www/dashboard, не из /root. После правки index_v2.html ОБЯЗАТЕЛЬНО прогон deploy_dashboard.sh — иначе кеш браузера vs stale файл."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

## Правило

После любой правки `/root/4BotsBybit-Trading/index_v2.html` (или `TRADING_DASHBOARD.html`) запусти:

```bash
bash /root/4BotsBybit-Trading/scripts/deploy_dashboard.sh
```

**Why:** nginx сервит из `/var/www/dashboard/{index,v2}.html` (root-mode permissions не дают symlink). До 2026-05-16 (commit `1d06c2f`) скрипт копировал ТОЛЬКО v1 (index.html). v2.html там был от 13 мая — все мои правки v2 не доходили до user'a, он видел кешированный stale файл. Из-за этого Артём не видел FORCE chips, real-defaults, force_grazed_tp1 counts.

**How to apply:** скрипт идемпотентен. Запускай после commit либо включи в commit workflow. Если правил `--check`-вариант покажет drift.

**Hard reload на маке:** даже после deploy браузер кеширует. Cmd+Shift+R / Ctrl+F5. Иначе user видит "цифры не появились" хотя они в JSON ответе уже есть.

## Внутри скрипта

```bash
declare -A PAIRS=(
  ["${REPO_DIR}/TRADING_DASHBOARD.html"]="/var/www/dashboard/index.html"  # v1
  ["${REPO_DIR}/index_v2.html"]="/var/www/dashboard/v2.html"              # v2
)
```

Оба пары копируются за один прогон. `--check` mode для проверки drift без копирования.

## Связано

- [[project-dashboard-v2]] — v1/v2 живут параллельно, карта endpoints
- [[feedback-dashboard-v1-v2]] — не путать v1 и v2 при правке
