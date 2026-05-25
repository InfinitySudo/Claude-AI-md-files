---
name: feedback-cockpit-unversioned
description: /var/www/dashboard/cockpit.html не в git — все правки только на диске. Backup перед правкой обязателен. Auto-mode classifier блокирует правки этого пути без явного allow от Артёма.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

`/var/www/dashboard/cockpit.html` — **unversioned prod**, не входит в `/root/4BotsBybit-Trading` репо. Правки **не пушатся в git**, живут только на диске VPS.

**Why:** dashboard cockpit разрабатывается итеративно и часто, любая правка сразу видна Артёму через `http://187.77.148.44:8080/cockpit.html`. Хранить в git избыточно.

**How to apply:**
1. Перед любой правкой — `cp /var/www/dashboard/cockpit.html /tmp/cockpit.html.bak_$(date +%Y%m%d_%H%M)`.
2. Auto-mode classifier **блокирует** правки этого пути без явного allow от Артёма. Текст «правь /var/www/dashboard/...» или «делай оба» — разблокирует.
3. nginx serves c `Cache-Control: no-store, no-cache, must-revalidate` (см. `/etc/nginx/sites-enabled/dashboard`), но Chrome всё равно кеширует — для verify говорить Артёму `Cmd+Shift+R`.
4. Если правка не отображается у Артёма — DevTools → Network → «Disable cache» + reload (это надёжно сбрасывает service-worker + http cache).

Связано: [[project-unversioned-prod-state]], [[project-dashboard-v2]].
