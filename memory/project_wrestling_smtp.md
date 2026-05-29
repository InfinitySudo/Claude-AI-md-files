---
name: project-wrestling-smtp
description: "Wrestling app SMTP: до 2026-05-29 НЕ был сконфигурирован → parental-consent и password-reset письма не отправлялись (код только print). Починено через systemd drop-in (Gmail borysiukartem55). Конфиг НЕ в git (секрет)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 9924a9cb-baa9-4aa6-aeee-d2beb8128b55
---

**Симптом (2026-05-29):** под-18 регистрируется → экран «Waiting for parent/guardian consent», но письмо родителю не приходит. Аккаунт не разблокируется. Та же причина ломала «Forgot password».

**Корень:** `backend/main.py` `_send_parental_consent_email` и `_send_reset_email` — best-effort SMTP, требуют env `WPT_SMTP_HOST/USER/PASS`. В systemd-юните их НЕ было → обе функции уходили в ветку `if not (...): print(...)` и письмо не слалось. Код корректен, не хватало только конфига.

**Фикс:** systemd drop-in `/etc/systemd/system/wrestling-api.service.d/smtp.conf` (права 600):
- `WPT_SMTP_HOST=smtp.gmail.com`, `WPT_SMTP_PORT=465`
- `WPT_SMTP_USER=borysiukartem55@gmail.com` + `WPT_SMTP_PASS=<gmail app password>` (взят из `/root/MypersonalAIassistent/.env` `GMAIL_APP_PASSWORD` — это аккаунт Артёма, он же `WPT_ADMIN_EMAIL`)
- `WPT_SMTP_FROM=Constant Wrestling <borysiukartem55@gmail.com>`, `WPT_BASE_URL=https://constantwrestling.cloud`
- `systemctl daemon-reload && restart wrestling-api`.

Рядом уже жил `vapid.conf` drop-in — drop-ins это штатный паттерн для wrestling-api.

**Проверено:** прямой smtplib-тест доставил письмо; live-регистрация под-18 (parent=borysiukartem55) прошла без SMTP-ошибок в логах → письмо ушло. Реально письмо приходит **с borysiukartem55@gmail.com** (не constantcwc), т.к. так аутентифицируемся в Gmail.

⚠️ **Конфиг unversioned (на сервере, секрет)** — в git его нет. При пересоздании VPS/юнита восстановить drop-in вручную. Если менять отправителя на constantcwc@gmail.com — нужен app password ИМЕННО того аккаунта.

См. [[project-wrestling-account-deletion]], [[feedback-cockpit-unversioned]] (тот же класс: важный server-config вне git).
