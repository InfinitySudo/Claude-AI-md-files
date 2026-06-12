---
name: feedback_logout_network_blip
description: OnTime вылетал в логин после простоя — сетевой сбой при resume стирал валидный токен; не трогать токен на network-ошибках
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5b904a97-9e9f-4dd3-8802-6c3fef431230
---

OnTime PWA выкидывал юзеров в окно логина после нескольких часов без активности (телефон + Mac).

**Причина (НЕ истечение токена):** JWT был 72ч, секрет `TSA_JWT_SECRET` стабильно зашит в systemd-юните (рестарты не инвалидируют). При «пробуждении» приложения первый `api.me()` падал с **сетевой** ошибкой (радио/PWA cold start не готовы), а `App.jsx` в `.catch` делал `removeItem('tsa_token')` + redirect на /login — то есть «на секунду offline» трактовалось как «auth failed».

**Фикс (commit c90fb02):**
- `src/api/client.js` `request()`: оборачивает `fetch` в try/catch; сетевой сбой кидает `err.network=true` и НЕ трогает токен. Только реальный 401 чистит токен (`err.auth=true`).
- `src/App.jsx` bootstrap: на `err.network` — сохраняет сессию и ретраит с backoff (cap 15s), не редиректит; логин только на genuine auth.
- TTL 72ч → 30 дней (`TSA_JWT_EXPIRE_HOURS`, дефолт 720).

**Why:** field-приложение, постоянные релогины бесят; дроп запроса ≠ невалидный токен.

**How to apply:** никогда не удаляй токен / не редиректь на логин по любой ошибке fetch — только по HTTP 401. Сетевые ошибки = ретрай, токен живёт. После деплоя юзер должен **один раз** перелогиниться (новый бандл + 30-дневный токен).
