---
name: OnTime Invite Codes
description: Где хранятся коды приглашения для самостоятельной регистрации по ролям
type: reference
originSessionId: 7307290c-93f4-4995-a318-269609a49e02
---
**Файл:** `/root/ontime/backend/.env.bot` (читается systemd-юнитом `ontime-api` через `EnvironmentFile=-`).

**Переменные и какую роль «открывают»:**
- `TSA_ADMIN_INVITE_CODE` → role=admin
- `TSA_FOREMAN_INVITE_CODE` → position=foreman
- `TSA_SERVICE_INVITE_CODE` → position=service
- `TSA_DELIVERY_INVITE_CODE` → position=delivery
- `TSA_ACCOUNTANT_INVITE_CODE` → role=accountant (добавлен 2026-04-20; бухгалтер, как и админ, минует roster-проверку; имеет доступ к payroll/QB экспортам через `require_finance`)

**installer/helper** — код не нужен, но регистрация валидирует по `roster` (админ заводит заранее).

**Why 4 разных кода, а не один:** admin может выдать foreman-код, не раскрывая admin-ключи. Кросс-подстановка блокирована: бэк проверяет код именно против той переменной, которой соответствует выбранная position. Vздать admin-код в поле foreman-invite бесполезно.

**How to apply:** При запросе "скажи код для X" — ЧИТАТЬ значение из `.env.bot`, не помнить (коды ротируются). При ротации — правишь файл + `systemctl restart ontime-api`.
