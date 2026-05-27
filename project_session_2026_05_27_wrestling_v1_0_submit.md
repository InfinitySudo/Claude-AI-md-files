---
name: project-session-2026-05-27-wrestling-v1-0-submit
description: "Wrestling-Performance-Tracker v1.0 отправлен в App Store (Submission ID acf3e653-945d-4d42-b25e-725d6d081e58, build 79860157 = Codemagic build #8, commit 2385b9b). v1.0.1 backbone (Sparrings location + cross-club apply flow) уже задеплоен на prod web."
metadata: 
  node_type: memory
  type: project
  originSessionId: d7e05049-6804-46d2-8613-1a002273082b
---

## Submission
- **App**: Constant Wrestling (`cloud.constantwrestling.app`, Apple ID `6773493168`).
- **Submission ID**: `acf3e653-945d-4d42-b25e-725d6d081e58` (26 May 2026 23:50 MDT).
- **Build attached**: TestFlight 79860157 (Codemagic build #8, commit 2385b9b).
- **Release mode**: Manual (Артём жмёт «Release this version» в пятницу).
- **Pending**: Expedited Review request (отдельно через ASC → Contact Us → App Review). Без него Apple обычно даёт 24-48ч ревью; expedited подкручивает до 6-12ч.

## v1.0 фиксы по дороге (build #5..#8)
- `33902d4` — manual code signing identities в codemagic.yaml.
- `3bcdf22` — APP_STORE_APP_ID=6773493168.
- `a5ca833` — show/hide password toggle в LoginPage.
- `b87a5d6` — Capacitor wrapper использует абсолютный `https://constantwrestling.cloud/api` (в `/api` не резолвится из `capacitor://localhost`).
- `52cec8c` — Forgot Password ведёт на TG/email админа (SMTP не настроен, чтобы reviewer не получил dead-end).
- `1210114` — убрали NSUserTrackingUsageDescription из Info.plist + sed-step `TARGETED_DEVICE_FAMILY = "1"` (iPhone only, чтобы Apple не требовал iPad screenshots).
- `2385b9b` — backend `update_match_meta` 500 fix (`multiple assignments to same column timer_running` при ended+timer_running) + убрали Лиги из nav (redirect /leagues → /) + UWW scoreboard mobile UX: bigger event log (12-13px, 44px height) + bottom-anchored Back button в safe-area.

## v1.0.1 backbone (commit `8ff3456`) — уже на prod web
**БД:**
- `tournaments` + country/region/city/description/contact_phone/contact_email/contact_social/cost_usd/max_spots/age_groups (csv)/is_public + index по country.
- Новая `tournament_applications` (UNIQUE(tournament_id, applicant_user_id) для idempotent re-apply, status pending/approved/rejected, payment_confirmed).

**Endpoints (`backend/main.py`):**
- `GET /api/tournaments?scope=public&country=X` discovery list.
- `GET /api/tournaments/public/countries` dropdown.
- `POST /api/tournaments/{id}/applications` apply (idempotent via ON CONFLICT).
- `GET /api/tournaments/{id}/applications` owner panel.
- `GET /api/applications/mine` applicant list.
- `PATCH /api/applications/{aid}` owner approve/reject/payment_confirmed.

**UI (`src/pages/TournamentsPage.jsx`):**
- Create-form: Country/Region/City/Phone/Email/Social/Cost/Max_spots/Age_groups multi + Public toggle.
- `DiscoverPublicSparrings` card (по дефолту страна = club.country).
- `ApplyModal` — атлеты из ростера + free-text emails + сообщение.
- `MyApplicationsCard` — статус + Pay-кнопка если payment_link задан.
- `SparringApplicationsPanel` внутри TournamentDetail (owner only).

**Codemagic build #9** автоматически собирается из `8ff3456` — после Apple одобрит v1.0 → submit v1.0.1 как обновление.

## Что остаётся Артёму
1. **Expedited Review** — ASC → Contact Us → App Review → Request Expedited (обоснование `Friday 29 May 2026 coordinated public launch`). До утра можно отложить.
2. **iOS-баннер на сайте** — после Apple approve поменять `IOS_APP_STORE_URL` в `src/components/IOSAppBanner.jsx` на `https://apps.apple.com/ca/app/constant-wrestling/id6773493168`. См. [[project-wrestling-mobile-launch]] шаг 11.5.
3. **Release this version** в пятницу когда статус `Pending Developer Release`.

## Подводные камни этой сессии
- Capacitor WebView ломал login (relative `/api` → `capacitor://localhost/api/...` → пустой response → `null.token`). Fix — детект `window.Capacitor` и абсолютный URL.
- NSUserTrackingUsageDescription без реального ATT prompt = Apple требует disclosure в App Privacy «Tracking». Никогда не добавлять в Info.plist пока не используешь `requestTrackingAuthorization()`.
- Capacitor template ставит `TARGETED_DEVICE_FAMILY = "1,2"` (universal). Без iPad screenshots Apple reject. Force iPhone-only через sed-step после `cap sync ios`.
- SMTP не настроен на prod — Forgot Password нужно либо убрать, либо переделать в TG/email админ-контакт (так и сделали в `52cec8c`).
- ASC поле «Описание» и «Примечания» легко перепутать — Артём вписал Notes for reviewer в Description, пришлось менять. Notes for reviewer = только Apple, Description = публичная страница в Store.
- ASC age-rating новая шкала 13+/16+/18+ (не 12+/17+).
- Codemagic auto-trigger иногда подвисает после push, нужен ручной Start new build.
- Backend `update_match_meta`: формирование UPDATE через list-append гнало `SET col = %s, col = %s` при ended+timer_running в одном PATCH. Решение — собирать column→fragment в dict, потом dump.

## Что НЕ помещалось в v1.0 → v1.0.1
- Sparrings location + cross-club apply flow — backbone готов, нужно проверить UX на iPhone.
- Лиги обратно (отдельный v1.0.2 update).
- SMTP password-reset.
- Push-уведомление owner-у про новые applications.

Связано: [[project-wrestling-mobile-launch]], [[project-wrestling-v2]], [[project-session-2026-05-26-wrestler-card-competitions]].
