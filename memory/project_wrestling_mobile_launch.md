---
name: project-wrestling-mobile-launch
description: "Wrestling-Performance-Tracker готов к публикации в AppStore/GooglePlay. Capacitor v7 + Android платформа + signed AAB локально на VPS. iOS через Codemagic cloud-Mac (без личного Mac). От Артёма: Apple Dev ($99/yr) + Google Play ($25) + Codemagic free."
metadata: 
  node_type: memory
  type: project
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

## Текущий статус (2026-05-24, commit fc7b403 в InfinitySudo/Wrestling-Performance-Tracker)
Готово на VPS, без Mac:
- `capacitor.config.json`: appId `cloud.constantwrestling.app`, name «Constant Wrestling», плагины Splash/StatusBar/Keyboard/Push.
- `resources/icon.png` (1024×1024) + `splash.png`/`splash-dark.png` (2732×2732) master assets.
- Capacitor v7 + плагины (`@capacitor/android/ios/splash-screen/status-bar/keyboard/assets`).
- **`android/` платформа** сгенерирована, иконки/splash раскатаны во все densities. Signing configs читают env-vars.
- **Signed release AAB** — `android/app/build/outputs/bundle/release/app-release.aab` (11 MB) — подписан keystore'ом `/root/secrets/constantwrestling-release.jks` (SHA1 `44:92:46:30:40:73:37:B1:A1:64:07:6D:F4:65:4F:7D:4C:59:DA:D4`, пароли в `/root/secrets/constantwrestling-release.env` chmod 600).
- Privacy Policy → `https://constantwrestling.cloud/legal/privacy.html`
- Terms of Service → `https://constantwrestling.cloud/legal/terms.html`
- `marketing/store_copy.md` — store-listing copy на 5 языках (EN+RU+PL+ES+UK) + Apple Privacy Manifest + Google Play Data Safety.
- `codemagic.yaml` — workflow для iOS (cloud Mac mini M2 → IPA → TestFlight автозагрузка) и Android (linux → AAB → Internal track). Триггер на push в master.
- `README_MOBILE_LAUNCH.md` — пошаговый guide.

VPS-stack: OpenJDK 21 (apt), Android SDK 34 в `/opt/android-sdk/` (cmdline-tools + platforms;android-34 + build-tools;34.0.0).

## От Артёма требуется (~30 минут активной работы + 1-3 дня verification)
1. **Apple Developer Program** — `https://developer.apple.com/programs/enroll/` $99/год, individual (не company → без D-U-N-S). Photo of government ID + selfie.
2. **Google Play Console** — `https://play.google.com/console/signup` $25 one-time, personal account.
3. **Codemagic** — `https://codemagic.io` (free tier 500 build-min/мес).
4. После регистрации: App Store Connect API key + Google Play Service Account JSON → загрузить в Codemagic как integrations. Keystore `/root/secrets/constantwrestling-release.jks` → загрузить как `keystore_constantwrestling`.
5. Push любой коммит в master → автобилд iOS+Android.

**Mac у Артёма НЕ нужен** — Codemagic арендует cloud-Mac под капотом. Mac включённый держать никогда не надо. Бэкенд `constantwrestling.cloud` (VPS) обслуживает app у юзеров 24/7 независимо.

## Грабли Apple (что добавит дни)
1. Sign in with Apple обязателен если есть Google/Facebook OAuth (`npm i @capacitor-community/apple-sign-in`).
2. «Mostly web» rejection — у нас есть native plugins (Push, Splash, StatusBar, Keyboard). На review-info написать что это native iOS app via Capacitor.
3. Privacy Manifest `PrivacyInfo.xcprivacy` обязателен с 2024.
4. Wrestling-app + minors → COPPA-compliance section, age rating.

## Backup-критично
- `/root/secrets/constantwrestling-release.jks` — keystore. **Без него обновления для Google Play невозможны навсегда**. Бэкап в 1Password / iCloud Drive обязателен.
- `/root/secrets/constantwrestling-release.env` — пароли. Тоже бэкап.

Связано: [[project-wrestling-v2]], [[project-wrestling-i18n-10langs]], [[project-wrestling-camp-payment]].
