---
name: project_ontime_doc_share_drive
description: "OnTime Documents — раздача blueprint (TG/email/print/Drive), per-user отправитель, тяжёлые файлы ссылкой, Drive ждёт OAuth-ключи"
metadata: 
  node_type: memory
  type: project
  originSessionId: b354475f-dafb-44cb-81e4-96365d15d001
---

OnTime вкладка Documents (2026-06-11): foreman/crew могут получать blueprint, и раздавать его.

**Раздача файла** (кнопки на карточке `DocumentCard`): Скачать · Печать · Telegram (всем на объекте через бота OnTime, `send_document_to_chat`) · Email · Сохранить на Google Drive. Авто-пуш: новый/обновлённый blueprint при загрузке шлётся бригаде в TG + алерт форману (`_auto_push_document`, категория в `AUTO_NOTIFY_DOC_CATEGORIES`).

**Per-user отправитель email** (`_send_email` + `_smtp_identity_for`):
- Учётки Артёма Борысюка (`ARTEM_SENDER_EMAILS` = artempm@/borysiukartem55@/borysiukartem1990@) → аутентификация SMTP как **artempm@threestonesalliance.ca**, From = artempm@. Пароль — Gmail app-pass, скопирован из `@solo_inboxBot` (`/root/MypersonalAIassistent/.env` ACCOUNT_3_PASS) в OnTime `.env.bot` как `ONTIME_SMTP_ARTEM_USER/PASS` (без пробелов!). ⚠ id=86 artem@threestonesalliance.ca — это Ткаченко, НЕ Артём.
- Остальные → дефолтный ящик materials@ + `Reply-To` = email отправителя (своим ящиком аутентифицироваться нельзя).

**Тяжёлые файлы в email**: Gmail режет сообщение на 25МБ, base64 раздувает ×4/3 → файл >~18МБ (`SAFE_EMAIL_ATTACH_BYTES`) рвал коннект (`SMTPServerDisconnected 'Server not connected'` — это была причина бага). Теперь >18МБ шлётся ссылкой: Drive-ссылка если Drive подключён, иначе подписанная login-free OnTime-ссылка `/api/documents/{id}/dl?exp&sig` (HMAC от JWT_SECRET, живёт 14 дней).

**Google Drive** (`backend/google_drive.py`, httpx, scope drive.file): ПОДКЛЮЧЕНО 2026-06-11, аккаунт artempm@threestonesalliance.ca. OAuth **Web**-клиент в проекте Google Cloud `ontime-499115` (redirect `https://ontime.management/api/integrations/google/callback`), `GOOGLE_OAUTH_CLIENT_ID/SECRET` в `.env.bot`. Приложение в режиме Testing → при авторизации экран «app not verified» (Advanced→continue), нужен test user. Refresh-токен в таблице `app_integrations`. Кнопка «Подключить Google Drive» (management) в шапке Documents даёт consent-ссылку. Опц. `GOOGLE_DRIVE_FOLDER_ID` — папка назначения. Загруженные файлы шарятся anyoneWithLink-reader.

Связано: [[feedback_dashboard_startup]], [[project_mai_assistant]] (источник app-паролей), [[project_tsa_timeline]].
