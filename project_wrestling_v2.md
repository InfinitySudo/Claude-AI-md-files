---
name: Wrestling App v2 — Multi-club + Full Features
description: Major v2 rewrite done 2026-04-13; multi-club, proportional norms, analysis, profile with socials, club branding
type: project
originSessionId: 4bf9c010-6bf6-4410-b91f-d3731633751f
---
## Wrestling Performance Tracker v2

### Что сделано (2026-04-13)

**Мультиклуб:**
- Таблица `clubs` (name, city, owner_coach_id, invite_code)
- Коуч при регистрации создаёт клуб (club_name + city обязательны)
- Атлет регистрируется по invite-коду клуба
- Все запросы фильтруются по club_id — полная изоляция
- `POST /api/clubs/regenerate-invite` — генерация нового кода

**Нормативы (переработаны):**
- Коуч создаёт: name, target_value, max_points (кнопки +/-)
- `publish_to_club=true` → создаёт для всех атлетов клуба
- Атлет вводит actual_value → `POST /api/norms/{id}/submit`
- Баллы = `min(max_points, (actual/target) × max_points)` — пропорционально
- Коуч confirm/reject → `POST /api/norms/{id}/confirm`
- Статусы: pending → submitted → confirmed/rejected

**Анализ тренировок:**
- Атлет выбирает тренировку + пишет текст → `POST /api/analysis`
- Коуч видит все submitted, ставит баллы + комментарий → `PATCH /api/analysis/{id}/review`
- Атлет видит отзыв и баллы

**Тренировки (расширены):**
- Поля: title, session_date, group_name, description
- QR-код автоматически (4 часа)

**Профиль атлета:**
- Фото (upload), имя, дата рождения, весовая категория, вес
- Соцсети: Instagram, TikTok, YouTube, Telegram, WhatsApp, Facebook
- Share Card: `GET /api/profile/card/{user_id}` (публичный)
- Ранг: Bronze(0-49) / Silver(50+) / Gold(100+) / Champion(200+)

**Баллы из 3 источников:**
- Нормативы: пропорционально (max задаёт коуч)
- Анализ: оценка коуча (0-N)
- Посещения: 1 за check-in

**Брендинг Constant Wrestling:**
- Логотип клуба: icon-192.png, icon-512.png (PWA иконки)
- Фон app: bg-watermark.png (красный волк, 10% opacity, cover)
- Фон логина: bg-login.png (20% opacity)
- Хедер: логотип + "Constant Wrestling"
- Источник: Google Drive файл с 5 вариантами логотипа

**Фронтенд:**
- LoginPage: выбор роли, коуч→создание клуба, атлет→invite код
- CoachDashboard: invite-код, создание тренировок/нормативов, confirm/reject, review analysis
- AthleteDashboard: 4 таба (Home/Norms/Analysis/Profile), bottom nav
- RankingsPage: лидерборд с разбивкой баллов по источникам
- Удалять участников может только coach

**Удаление аккаунта:**
- Только coach может удалять участников
- Атлет НЕ может удалить сам себя (убрано по запросу Артёма)

### Ключевые файлы
- Backend: `/root/Wrestling-Performance-Tracker/backend/main.py`
- API client: `/root/Wrestling-Performance-Tracker/src/api/client.js`
- Frontend pages: `src/pages/` (Login, CoachDashboard, AthleteDashboard, Rankings, Members, Tournaments, Analytics, Session)
- Assets: `public/` (icon-192, icon-512, bg-watermark, bg-login, club-bg.jpg)
- URL: constantwrestling.cloud
- API: port 8001, systemd: wrestling-api

**Why:** Артём — тренер wrestling клуба Constant Calgary Wrestling Club, приложение для управления клубом и мотивации спортсменов.
**How to apply:** nginx проксирует /api/ на :8001; `npm run build` деплоит в dist/; `sudo systemctl restart wrestling-api` для бэкенда.
