---
name: reference_codemagic_api
description: Codemagic API token + appId/workflow для Wrestling — запуск и проверка iOS/Android сборок
metadata: 
  node_type: memory
  type: reference
  originSessionId: f7728df3-cc3b-4069-9d7d-15de2f92e572
---

Codemagic (Wrestling-Performance-Tracker) — Артём дал доступ, использовать когда просит или нужно проверить/запустить сборку.

- **API token (x-auth-token):** `h_VJ1qAVAW3eTdSuFZh7iZyryIrxB0get0HMeOVqB24`  ⚠️ секрет
- **appId:** `6a160ee7c6a5628537fe1a51`
- **yaml workflow ids:** `android-playstore`, `ios-testflight`
- **branch:** `main`

Использование:
- список сборок: `curl -s -H "x-auth-token: $T" https://api.codemagic.io/builds?limit=8`
- старт: `POST https://api.codemagic.io/builds` body `{"appId":"...","workflowId":"android-playstore","branch":"main"}`
- статус: `GET https://api.codemagic.io/builds/<buildId>` → поле `message` содержит причину падения

⚠️ Автозапуск по git push в `main` НЕ срабатывает (хотя в codemagic.yaml `triggering: push main`) — запускать сборку вручную через API.

Управление env-переменными через API (работает): `POST/GET/DELETE /apps/<appId>/variables`, body `{"key","value","group","secure"}`. App-level groups сейчас: только `android_keystore`.

✅ БЛОКЕР Android РЕШЁН (2026-06-12, build 6a2c3d22 finished, AAB 11.7МБ):
- keystore залит НЕ как code-signing identity, а как base64-секрет: group `android_keystore` → `ANDROID_KEYSTORE_B64`/`ANDROID_KEYSTORE_PASSWORD`/`ANDROID_KEY_ALIAS=upload`/`ANDROID_KEY_PASSWORD` (значения = `/root/secrets/constantwrestling-release.env`).
- codemagic.yaml: убран `android_signing: [keystore_constantwrestling]`; добавлен шаг «Decode keystore» (base64 → upload.jks → `ANDROID_KEYSTORE_PATH` в `$CM_ENV`); build.gradle уже читал `ANDROID_*`.
- `instance_type: linux_x2` НЕдоступен на текущем billing-плане → переключено на `mac_mini_m2` (как iOS).
- ✅ Google Play АВТО-ПУБЛИКАЦИЯ РАБОТАЕТ (2026-06-12, build 6a2c48e9 Publishing→success): secret `GCLOUD_SERVICE_ACCOUNT_CREDENTIALS` (secure, group `google_play_credentials`) = JSON сервис-аккаунта `codemagic-play-publisher@constant-wrestling.iam.gserviceaccount.com` (GCP проект `constant-wrestling`, копия `/root/secrets/constant-wrestling-play-publisher.json`). Аккаунт приглашён в Play Console (Users & permissions, Admin на приложение). Play Android Developer API включён в проекте.
- codemagic.yaml publishing: `google_play` → `track: alpha`, `submit_as_draft: false` (commit c9543c0). Тестеры закрытого теста сидят на стандартном треке `alpha` (НЕ кастомный); каждый успешный билд авто-раскатывается им live. Продакшн НИКОГДА не авто — promote alpha→production вручную. Трек подтверждён через сервис-аккаунт (androidpublisher edits API).
- Список треков сейчас: alpha=v3 (1.0.2 completed), internal=v4 (1.0.3 draft, мусор от теста — можно игнор).
- ⚠️ каждый билд требует НОВЫЙ versionCode (Play не принимает дубль даже в другом треке). Бамп vCode в android/app/build.gradle перед сборкой. Сейчас занято 3 (alpha) и 4 (internal draft) → следующий ≥5.
- Проверить треки/релизы программно: `google-auth` (pip --break-system-packages) + key `/root/secrets/constant-wrestling-play-publisher.json`, scope androidpublisher, POST edits → GET edits/{id}/tracks.
- Локальная сборка тоже работает: `cd android; set -a; . /root/secrets/constantwrestling-release.env; set +a; ANDROID_HOME=/opt/android-sdk ./gradlew bundleRelease`.

Ключ подписи (ОБЯЗАН совпадать с Play 1.0.1): alias `upload`, SHA-256 `73:F7:ED:48:64:48:F2:C4:E8:72:37:8D:AA:AB:11:80:DE:AF:51:42:E0:3E:07:D5:32:A3:09:AB:01:2E:F8:83`. См. [[project_wrestling_play_closed_test]], [[project_wrestling_mobile_launch]].
