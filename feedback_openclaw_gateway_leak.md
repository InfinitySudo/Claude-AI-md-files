---
name: feedback_openclaw_gateway_leak
description: openclaw-gateway.service течёт по памяти (~4ГБ за 2.5 дня); рестарт + добавлен swap 4ГБ на srv1476476
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 64d74dce-2f63-4fe9-8812-50d52a2470ec
---

VPS `srv1476476` (187.77.148.44, 16 ГБ RAM) — я работаю прямо на этом хосте, SSH не нужен (локальные команды).

**СТАТУС 2026-05-30: ВЫКЛЮЧЕН по просьбе Артёма** (он им не пользуется) — `systemctl --user stop` + `disable`, теперь inactive+disabled, после ребута не поднимется. Чтобы вернуть: `XDG_RUNTIME_DIR=/run/user/0 systemctl --user enable --now openclaw-gateway.service`.

**Симптом (был):** `openclaw-gateway.service` (node, v2026.4.2, systemd **user**-unit под root) медленно течёт — набил **4.1 ГБ за 2.5 дня** аптайма. После рестарта сразу ~350-430 МБ.

**Why:** утечка в самом gateway; без свопа риск OOM-kill торговых ботов.

**How to apply:**
- Рестарт: `XDG_RUNTIME_DIR=/run/user/0 systemctl --user restart openclaw-gateway.service`
- 2026-05-30 добавлен swap: `/swapfile` 4ГБ в `/etc/fstab`, `vm.swappiness=10` в sysctl.conf.
- Если снова раздуется за пару дней — повесить авто-рестарт по памяти (systemd `MemoryMax=` или cron-watchdog).

OpenClaw = параллельный агент на этом же VPS — см. [[feedback_parallel_agents]]; рестарт согласовывать (затрагивает его сессию).
