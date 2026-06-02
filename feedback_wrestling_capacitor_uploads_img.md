---
name: feedback_wrestling_capacitor_uploads_img
description: "Wrestling iOS — фото /uploads показывают \"?\" в нативном app (WebView перехватывает same-origin img); фикс fetch→blob, отложен в 1.0.1"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 64d74dce-2f63-4fe9-8812-50d52a2470ec
---

**Баг:** в нативном iOS-приложении Constant Wrestling аватары/фото профиля показываются как «?» (битая картинка). На десктоп- и мобильном **вебе** работают. Замечено 2026-05-30.

**Корень:** фото хранятся относительным путём `/uploads/xxx.jpg` (backend `main.py` upload_photo/upload_full_photo → `url=f'/uploads/{fname}'`). Capacitor (`capacitor.config.json`: `server.hostname=constantwrestling.cloud`, `iosScheme=https`, **нет `server.url`** → webDir:dist бандлится в app) — WebView перехватывает same-origin загрузки ресурсов (`<img src>`) и отдаёт из локального бандла, где `/uploads/` нет → 404 → «?». API при этом работает, т.к. `client.js` шлёт `fetch()` на `https://constantwrestling.cloud/api` по сети (XHR/fetch не перехватываются scheme-handler'ом, а `<img>` — да). `/uploads` публичны (StaticFiles, без токена, HTTP 200).

**Why не чинили сразу (2026-05-30):** шёл App Store ресабмит v1.0; фикс требует нового build (фронт вшит в бандл) → обнулил бы готовый сабмит и сорвал запуск 10:00 Calgary. Ревьюер под demo-аккаунтом фото не грузит → баг не видит → не блокер.

**ФИКС ГОТОВ (2026-05-30):** ветка `fix/avatar-capacitor-1.0.1`, commit `34c4115` (НЕ в main, НЕ собран в prod dist — сабмит v1.0 не тронут). Добавлен `src/components/NetImage.jsx`: вне Capacitor обычный `<img>` (с absolutize `/uploads`→ORIGIN), в нативе `fetch(абс.URL)→blob→createObjectURL`, при провале `onError()`→буква/плейсхолдер. Применён в ProfilePage (3 hero + 2 верхних аватара), AvatarCircle (покрывает списки), и прямых img в RankingsPage/TournamentsPage/LeaguesPage/LigaProPage/CoachDashboard(club logo)/AthleteDashboard/ClubPeopleSheet. Компиляция проверена `vite build` в /tmp (ок, 2123 модуля).

**Выкат в 1.0.1 (после апрува 1.0):** `git checkout main && git merge fix/avatar-capacitor-1.0.1` → bump version/build в Xcode-проекте → `npm run build` → `npx cap sync ios` → пересборка в Codemagic → загрузить новый build → выбрать его в новой версии 1.0.1. (Веб-прод обновится сразу после `npm run build` — это ок/желательно.)

Связано: [[project_session_2026_05_27_wrestling_v1_0_submit]] (Capacitor URL грабли), [[feedback_nginx_uploads_regex_trap]].
