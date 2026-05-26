---
name: feedback-cockpit-unversioned
description: /var/www/dashboard/cockpit.html не в git — все правки только на диске. Backup перед правкой обязателен. Auto-mode classifier блокирует правки этого пути без явного allow от Артёма.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

`/var/www/dashboard/cockpit.html` — **unversioned prod**. Есть **дублирующий source** `/root/Space_Live/public/cockpit.html` в git (InfinitySudo/Space_Live), но **они часто расходятся**: горячие правки (ZEN/HIDE hotkeys, `.stage { bottom: 28px }` full-screen, elliptical orbit clamp, `__rebuildOrbital`) ложатся только в prod.

**Why:** dashboard cockpit разрабатывается итеративно. Артём видит правку сразу через `http://187.77.148.44:8080/cockpit.html`. Раньше prod и source были одной копией, потом prod ушёл вперёд.

**How to apply (ВАЖНО — урок 2026-05-26):**
1. Перед любым `cp source → prod` — **СНАЧАЛА `diff /var/www/dashboard/cockpit.html /root/Space_Live/public/cockpit.html`**. Если в prod есть unversioned-фичи которых нет в source — НЕ перезаписывай, сначала перенеси их в source. В прошлый раз я затёр ZEN/HIDE + planet-orbit fix таким copy и Артёму пришлось разгребать.
2. Перед правкой prod — `cp /var/www/dashboard/cockpit.html /tmp/cockpit.html.bak_$(date +%Y%m%d_%H%M)`.
3. Auto-mode classifier **блокирует** правки `/var/www/dashboard/*` без явного allow от Артёма. Слова «правь prod», «делай оба», «udali starie» — разблокируют.
4. nginx serves c `Cache-Control: no-store, no-cache, must-revalidate` (см. `/etc/nginx/sites-enabled/dashboard`), но Chrome всё равно кеширует — для verify говорить Артёму `Cmd+Shift+R` или открыть `?v=<git-sha>`.
5. После любой правки prod — синхронизируй source: `cp /var/www/dashboard/cockpit.html /root/Space_Live/public/cockpit.html` + commit. Drift между source и prod = catastrophic-затирание при следующем copy.

Связано: [[project-unversioned-prod-state]], [[project-dashboard-v2]], [[project-cockpit-zen-mode]].
