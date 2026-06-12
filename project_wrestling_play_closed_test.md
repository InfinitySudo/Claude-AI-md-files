---
name: project-wrestling-play-closed-test
description: "Constant Wrestling — Google Play closed test (Alpha) статус, дедлайн 14 дней / 12 тестеров до продакшена"
metadata: 
  node_type: memory
  type: project
  originSessionId: cc08b35d-fb6b-4837-a3eb-798c71971731
---

Google Play публикация приложения **Constant Wrestling** (PWA в обёртке **Capacitor**, НЕ TWA; `capacitor.config.json` webDir=dist, `server.hostname` без `server.url` → ассеты **вшиты в бандл**, см. [[project-wrestling-v2]]).

⚠️ **Capacitor bundled-assets:** новые фичи попадают в установленное приложение Play/App Store ТОЛЬКО с новым билдом (npm run build → npx cap sync → новый AAB, version code 3+). Веб-версия constantwrestling.cloud обновляется сразу. Заливка нового билда в тот же closed-трек НЕ сбрасывает 14-дн окно. Сборка: `npm run mobile:build`, codemagic.yaml есть.

**2026-06-11 добавлено 5 фич (только веб, нужен новый билд для нативки):** B нормативы (unit_type sec_meters/sec_count + coach-ввод в матрице, таблицы norm_standards.unit_type/target_secondary/actual_secondary), A тренировки (session_extra_claims — спортсмен self-report доп.заданий+анализ→тренер подтверждает), C расписание кемпа (camp_schedule), D рассылка тренера (/api/broadcast) + ДР на весь клуб (был только тренерам), E месячная оплата (monthly_payments + $ badge в Layout жёлтый/зелёный, тренер тапает в MembersPage). Все на FastAPI backend/main.py + React pages. Коммит 0401230.

**2026-06-11 табло + медали (коммит 88c5777):** UWWScoreboard.jsx SideCard — диагональное фото бойца из профиля (clip-path, фото уже отдавал backend athlete1_photo/athlete2_photo) + счёт по центру свободной зоны (padding-сдвиг, НЕ absolute — absolute ломал поток и прятал кнопки +баллов!) + lower-third W-L·BW%·streak·медали (одноразовый /matches/{id}/wrestler-stats, не на поллинге). Медали: таблица wrestler_achievements (спортсмен submit pending → тренер approve, place 🥇🥈🥉+турнир+год+уровень), секция в ProfilePage Home (MedalsSection), счётчики в /wrestler-card и в стате матча. ⚠️ Урок: на табло держать score+кнопки В flex-потоке с z-10, фото фоном z-0.

**App:** Constant Wrestling · package/app id `cloud.constantwrestling.app` · legal-домен `constantwrestling.cloud`
**Track:** Closed testing — Alpha · релиз **1.0.1 (2) — first closed test** · bundle code 2, 10.8 MB · 177 стран

**Уже закрыто (по состоянию на 2026-06-11):**
- App content — все 10 деклараций (Privacy `https://constantwrestling.cloud/legal/privacy.html`, Data safety 3 типа данных + Account deletion URL `https://constantwrestling.cloud/legal/delete-account.html`, Content rating 3+, Target age 13+, Ads=нет, sign-in restricted)
- Store settings: категория **Sports**, feedback-email `borysiukartem55@gmail.com`
- Main store listing + графика залиты
- Email-список тестеров **«Constant Wrestling» = 13 адресов** (CSV без заголовка: `/root/constant_wrestling_emails.csv`; загрузчик Play отвергает строку `Email Address`)
- 2026-06-11 изменения отправлены на ревью (Managed publishing OFF → публикуется автоматически после одобрения)

**Чек-лист до продакшена (что ещё впереди):**
- [ ] Google одобрил closed-test релиз (статус In review → Approved)
- [ ] Со страницы Testers взять **opt-in ссылку** и разослать 13 тестерам
- [ ] **≥12 тестеров РЕАЛЬНО нажали opt-in + поставили приложение** (сейчас 0; счётчик 14 дней стартует с этого момента, НЕ с добавления email)
- [ ] Держать тест **≥14 дней** с ≥12 активными тестерами
- [ ] Затем **Apply for production** (ответить на вопросы про closed test)

⚠️ Главная ловушка: 14-дневное окно НЕ идёт, пока <12 человек реально opted-in. Добавить email ≠ opted-in. Гнать тестеров жать ссылку сразу после одобрения.

Файл прислан Артёму в TG ботом @DexClaudCodAIBot (token/owner в [[project-claude-telegram-bot]]).
