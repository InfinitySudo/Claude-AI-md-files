---
name: project_session_2026_05_30_wrestling_submit
description: "Сессия 2026-05-30 (прервана): Wrestling v1.0 ресабмит — новые скриншоты iPhone+iPad загружены, письмо ревьюеру, фикс аватарок готов на ветке для 1.0.1"
metadata: 
  node_type: memory
  type: project
  originSessionId: b2df2c3a-76aa-4633-8aa8-f7effcfd029d
---

Чекпойнт прерванной сессии 2026-05-30 (восстановлено в следующей сессии).

**Контекст:** Apple отклонил Constant Wrestling v1.0 (build 80028266) по Guideline 2.3.3 — скриншоты 6.7″/6.5″ iPhone показывали промо-картинки, не живой UI. Ревью шло на iPad Air 11″ M3. Submission ID `8c9a124f-bcb0-4873-bf1a-04d3b81901f8`.

**Сделано:**
1. Сгенерены реальные скриншоты приложения (см. [[project_wrestling_appstore_screenshots]]): iPhone 6.9″ (1290×2796), 6.5″ (1242×2688), iPad 13″ (2064×2752). Артём подтвердил загрузку iPhone обоих размеров в App Store Connect → «оба прошли без ошибок». iPad-комплект сгенерён и отдан; загрузка iPad на момент обрыва не подтверждена явно.
2. Составлено письмо ревьюеру (EN): просьба проверить сабмит целиком от начала до конца и дать **полный список** замечаний за один проход (а не по одному с задержкой 24ч); контекст — планировали запуск **сегодня 10:00 Calgary** для клуба (дети/атлеты/родители, дата анонсирована на родительском собрании). Тон мягкий, без требования «пропустить» проверку.
3. Фикс бага аватарок («?» в нативном iOS) подготовлен на ветке `fix/avatar-capacitor-1.0.1` (commit `34c4115`) — НЕ в main, сабмит v1.0 не тронут. Детали → [[feedback_wrestling_capacitor_uploads_img]].

**Осталось Артёму по v1.0:** в App Store Connect — Save в Media Manager → вставить письмо в «Ответ на проверку» → Submit for Review.

**После апрува 1.0:** выкатить 1.0.1 с фиксом аватарок (план в [[feedback_wrestling_capacitor_uploads_img]]).

**Замечание по чистке:** публичный `dist/appstore-ipad13-521d9cb6b0.zip` остался выложен (iPhone-zip уже удалён прошлой сессией). PNG-исходники сохранены локально в `review_screens/`, так что zip можно удалить — слетит при ближайшем `npm run build` в любом случае.

Связано: [[project_wrestling_appstore_screenshots]], [[feedback_wrestling_capacitor_uploads_img]], [[project_session_2026_05_27_wrestling_v1_0_submit]], [[project_wrestling_account_deletion]].
