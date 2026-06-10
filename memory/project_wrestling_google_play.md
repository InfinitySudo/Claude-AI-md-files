---
name: project-wrestling-google-play
description: "Constant Wrestling — запуск в Google Play (с нуля 2026-06-03). Individual-аккаунт, age-gate 13+, готовые ассеты + AAB versionCode 2, closed-testing 20 тестеров/14 дней. Что заполнять в Create app/Store listing."
metadata: 
  node_type: memory
  type: project
  originSessionId: bc80b216-c00f-4e7e-a577-045be28d70ce
---

## Google Play запуск — Constant Wrestling (старт 2026-06-03)

Связано: [[project-wrestling-mobile-launch]] (общий launch + keystore), [[project-wrestling-v2]], [[project-wrestling-camp-payment]].

### Аккаунт
- Play Console **Personal / Individual** аккаунт. **Account ID: 4901449532864858506**, developer name **Constant Wrestling**.
- Привязан к Google **borysiukartem55@gmail.com** (НЕ ...1990 — был риск выбрать не ту почту; принадлежность аккаунта менять нельзя навсегда).
- $25 разовый сбор оплачен 2026-06-03. На 2026-06-03 **identity на верификации у Google** (1–3 дня, придёт письмо). Phone-verify авто-разблокируется после одобрения ID. **Create app залочен до прохождения верификаций.**
- Тип Individual выбран сознательно: нет юр.лица → не хотим **DUNS** (его требует ветка Organisation). Минус individual = правило 20 тестеров/14 дней (см. ниже).

### КЛЮЧЕВОЕ решение: age-gate 13+ (НЕ «designed for children»)
- Артём подтвердил: в app реально логинятся дети <13. Но чтобы остаться на individual-аккаунте и вне Google «Families/COPPA» (которое может требовать organisation-аккаунт), выбрали **Вариант A: позиционируем как 13+**, профили младше 13 ведёт тренер/родитель.
- В форме регистрации Play: App categories → **None of the above** (НЕ «Apps designed for children or families»); Target audience → **13+**.
- Под это **изменён код** (commit 57b1c09, ветка `fix/avatar-capacitor-1.0.1`):
  - `backend/main.py` `/api/auth/register`: отклоняет если age<13; DOB обязателен для athlete/guest.
  - `backend/main.py` `/api/auth/login`: не выдаёт токен если `needs_parental_consent=TRUE` и `parental_consent_at IS NULL` (раньше блок был только во фронт-роутах — дыра).
  - `src/pages/LoginPage.jsx`: флаг `under13`, красный блок, submit задизейблен.
  - backend уже задеплоен (systemctl restart wrestling-api) — действует для всех клиентов вкл. iOS.
- `marketing/store_copy.md` поправлен (commit dcd0178): убрана фраза «under 13 register with consent» → «регистрация с 13 лет» (иначе листинг противоречил коду).

### Готовые ассеты (commit dcd0178, в репо `/root/Wrestling-Performance-Tracker/`)
- AAB для загрузки: `android/app/build/outputs/bundle/release/app-release.aab` — **versionCode 2, versionName 1.0.1**, подписан keystore `/root/secrets/constantwrestling-release.jks` (alias `upload`, пароли в `...release.env`). Содержит свежий веб-бандл (avatar-фикс + age-gate). Сборка: `cd android; set -a; . /root/secrets/constantwrestling-release.env; set +a; export ANDROID_HOME=/opt/android-sdk; ./gradlew bundleRelease --no-daemon`.
- Google Play графика в `marketing/google_play/`: `icon-512.png` (512×512), `feature-graphic-1024x500.png`, `phone/` (8 скриншотов 1242×2688 — переиспользованы iOS 6.5).
- Текст листинга: `marketing/store_copy.md` (EN/RU/PL/ES/UK + Google Data Safety секция).

### Cheat-sheet для Create app / Store listing
- App name **Constant Wrestling**; App; Free; default lang English (US).
- Short desc (≤80): `Run your wrestling club from one screen — athletes, norms, rankings.`
- Full desc: EN-блок из store_copy.md. Category **Sports**. Email borysiukartem55@gmail.com.
- Privacy `https://constantwrestling.cloud/legal/privacy.html`, Terms `.../legal/terms.html` (оба отдают 200).
- Data safety: собираем Email, Name, Photo(avatar), User ID, Crash data; encrypted in transit (HTTPS); удаление аккаунта в app (Profile→Delete) + email; данные не продаём/не шерим для рекламы.
- App access (для ревью): `demo-promo@constantwrestling.cloud` / `DemoReview2026!` (+ demo-athlete-1/-2 тем же паролем).
- Earning money: **Yes → Other** (Square camp payments — реальная услуга, внешний платёж легален). Подписку на функции, если будет → ОБЯЗАНА идти через Google Play Billing, не Square.

### Прогресс 2026-06-09 (App content + релиз заведён)
- **Все 10 деклараций App content ЗАКРЫТЫ** («You've caught up with everything»): Privacy policy, Ads=No, Sign-in details (demo-promo creds + full-access чек), Content ratings (IARC → Everyone/PEGI 3, категория «All other app types»), Target audience (13–15/16–17/18+, appeal to children=No), Data safety, Advertising ID=No (нет ads-SDK, AD_ID нет в merged manifest), Government=No, Financial features=None, Health=None.
- **Data safety**: собираем Name/Email/User IDs (App functionality+Account management, required, не ephemeral) + Photos (App functionality, **Users can choose** — аватар опционален) + Crash logs (Analytics); encrypted in transit=Yes; не шерим третьим лицам; удаление аккаунта=Yes по URL ниже.
- **Delete account URL** (требует Data safety): создал `public/legal/delete-account.html` (in-app Profile→Delete + email constantcwc@gmail.com), задеплоен в `dist/legal/` (nginx), коммит **c9b9869** ветка `fix/avatar-capacitor-1.0.1`. URL: `https://constantwrestling.cloud/legal/delete-account.html`. Реальная функция удаления подтверждена в коде: фронт ProfilePage.jsx `DELETE /api/me?confirm=true` → backend `@app.delete('/api/me')` main.py:2630.
- **Closed testing track «Alpha»**: драфт-релиз **1.0.1 (2)** создан (AAB залит), страны = Select all, release notes заполнены. **ЗАСТРЯЛИ на шаге Testers**: нужно ≥12 email’ов в Email list + feedback email constantcwc@gmail.com, затем Send for review.
- ⚠️ Тестерам нужны именно их **email-адреса** (Google-аккаунты) — opt-in ссылка одна не работает, Google сверяет email открывшего по списку.

### Closed testing (обязательно для individual, до production)
- ⚠️ ОБНОВЛЕНО 2026-06-09: Google снизил порог до **≥12 тестеров** (раньше было 20), реально opted-in по ссылке, держать **непрерывно 14 дней** → потом «Apply for production access» → ревью несколько дней. Дашборд показывает «at least 12 testers».
- 14-дневный отсчёт стартует **от момента вступления 12 тестеров**, не от регистрации аккаунта.
- Тестеры — **только @gmail.com / Google-аккаунт** и **Android** (iPhone не считается). Цель ≈25 с запасом.
- Opt-in ссылка (`play.google.com/apps/testing/cloud.constantwrestling.app`) появляется ТОЛЬКО после Create app → Closed testing track → добавления тестеров. Рекомендация: собрать тестеров в **Google Group**, одну группу добавить в трек.
- Сообщения для клубного чата (RU/EN сбор Gmail + инвайт с opt-in) уже составлены в этой сессии.

### Сроки / грабли
- Individual первый релиз по календарю ≈ **14 дней теста + неск. дней ревью** ≈ 2.5–3 недели. Organisation-аккаунт этого этапа не имеет (но нужен DUNS).
- iOS Codemagic-билд триггерится на push в **master**; age-gate сейчас в ветке `fix/avatar-capacitor-1.0.1` — для App Store нужно смержить в master (backend-правки уже live для всех).
- versionCode при каждом новом AAB должен расти (сейчас 2).
- keystore backup критичен — без него обновления Play невозможны навсегда.
