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

---

## 2026-05-26 — App Store launch prep (commit 204a370)
- `LAUNCH_FRIDAY.md` в repo — step-by-step что Артём должен сделать в ASC + Codemagic для пятничного релиза 29 May 2026.
- `public/legal/{privacy,terms}.html` обновлены под Constant ToS/Privacy (PIPEDA, Alberta law). URLs `constantwrestling.cloud/legal/{privacy,terms}.html` отдают 200 — Apple требует.
- `codemagic.yaml` теперь шаг **"Patch Info.plist"** вставляет все NS*UsageDescription + `ITSAppUsesNonExemptEncryption=false` автоматически на каждый iOS build → закрыты основные rejection-причины.
- Demo data на prod: `demo-promo@constantwrestling.cloud` / `DemoReview2026!` (coach, owner of "Demo Wrestling Club" id=6, invite `P7HF03PT`) + `demo-athlete-1` / `demo-athlete-2` тем же паролем. Seeded `/tmp/seed_demo.py` (idempotent — можно повторно запускать; пароли сбрасываются bcrypt'ом).
- Screenshots `marketing/screenshots/ios/{6.5,6.9}/` (5 PNGs each, web-viewport через Playwright).
- `marketing/store_copy.md` — appended "What's new v2026.05.29" + Apple Review notes (sign-in info + reviewer flow + export compliance + age rating 12+).

**Что осталось руками Артёму:**
1. ASC → API key (Admin) → Codemagic integration с именем точно `app_store_connect_artem`.
2. ASC → My Apps → New App для `cloud.constantwrestling.app`; забить `apple_id` в `codemagic.yaml` поле `APP_STORE_APP_ID`.
3. ASC fill metadata (Subtitle / Promotional / Description / Keywords / Privacy URL / Terms URL / Age 12+ / Category Sports → Health & Fitness) — текст в `store_copy.md`.
4. ASC upload screenshots из `marketing/screenshots/ios/`.
5. Push в master → Codemagic auto-build → TestFlight Internal → smoke на iPhone.
6. ASC → Submit for Review, выбрать **Manually release this version** (важно — иначе автоматически выкатится сразу после approve).
7. Optionally request expedited review с обоснованием "Friday 29 May coordinated launch".
8. Friday 29 May → Release this version → live через 1-24 ч.
