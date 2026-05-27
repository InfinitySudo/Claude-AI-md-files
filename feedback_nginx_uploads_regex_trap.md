---
name: feedback-nginx-uploads-regex-trap
description: "nginx `location ~* \\.(jpg|png|jpeg)$ {try_files $uri =404}` перехватывает /uploads/*.jpg и 404'ит — нужен `location ^~ /uploads/`"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c9d2b899-f272-4e25-b502-fa1e0f5284ca
---

В /etc/nginx/sites-enabled/wrestling был regex `location ~* \.(png|jpg|jpeg|svg|ico|woff2?)$ { try_files $uri =404 }` для immutable-кэша картинок в `/root/.../dist`. Этот regex имеет приоритет над голым префиксным `location /uploads/ { proxy_pass ... }`, поэтому **все** uploaded аватары (`/uploads/avatar_*.jpeg`) попадали в эту локацию и 404'ились (в dist таких файлов нет).

**Why:** В nginx порядок приоритета: `=` > `^~` > regex > обычный префикс. Голый префиксный location регекс перебивает.

**How to apply:** Когда добавляешь proxy_pass на /uploads/ (или любой подкаталог, который пересекается с regex-локациями), ставь `location ^~ /uploads/ { proxy_pass ... }` — это запрещает регекс-локациям перехватывать. Проверяется одной командой: `curl -sI https://host/uploads/<реальный_файл>` должен быть 200, а не 404. Связано: [[project_wrestling_v2]], [[feedback_dashboard_startup]].
