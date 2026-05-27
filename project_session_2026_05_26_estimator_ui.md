---
name: session-2026-05-26-estimator-ui
description: OnTime estimator UI улучшения — Feature Requests с фото + заметные кнопки в Memory разделе (commits 4f262e5..7d59e18)
metadata: 
  node_type: memory
  type: project
  originSessionId: 4e902f45-6b6d-4675-83eb-34c54b627a5e
---

# Сессия 2026-05-26 — OnTime Estimator UI polish

## Что сделано

### 1. Feature Requests раздел — создание из UI
**Раньше:** только TG-бот @TSA_EstimatorBot мог создавать. UI был read-only.
**Сейчас:** кнопка `+ New request` в шапке раздела + модалка с title/description/priority + multi-photo upload.

**Backend:**
- ALTER TABLE `estimator_feature_requests` ADD COLUMN `photos TEXT` (JSON-массив paths)
- `POST /api/estimator/feature-requests` теперь под `require_estimator` (для UI-формы)
- `POST /api/estimator/feature-requests/from-bot` — отдельный internal-only endpoint для TG-бота (no auth, только через 127.0.0.1)
- `POST /api/estimator/feature-requests/{fid}/photos` — multipart upload, JPEG resize до 1600px @ Q82
- `DELETE /api/estimator/feature-requests/{fid}/photos?file_path=...`
- LIST/PATCH endpoints парсят `photos` JSON в массив

**TG-бот:** `siding-estimator-bot/siding_tools.py` переключён на `/from-bot`.

**Frontend (`src/pages/FeatureRequestsPage.jsx`):**
- Фиолетовая кнопка `+ New request` в шапке
- `CreateRequestModal` с полями + multi-file picker
- Чипы выбранных файлов с X для удаления
- На карточках запросов — миниатюры фоток (clickable)

### 2. Memory раздел — заметные `+` кнопки
**Проблема:** старая серая `+` иконка справа от категории не выглядела кликабельной — Артём не понял что можно добавлять.

**Сейчас (`src/pages/EstimatorMemoryPage.jsx`):**
- Фиолетовая `+ New` кнопка в шапке (создаёт в Lessons по умолчанию)
- У каждой категории — purple-pill `+ Add` (вместо невидимой иконки)
- На пустом экране — 5 quick-add кнопок по категориям

## Файлы
- `/root/ontime/backend/main.py` — feature-requests endpoints
- `/root/ontime/src/pages/FeatureRequestsPage.jsx`
- `/root/ontime/src/pages/EstimatorMemoryPage.jsx`
- `/root/ontime/src/lib/i18n.js` — новые ключи `fr_*` и `est_memory_add_short`
- `/root/siding-estimator-bot/siding_tools.py` — переключение на `/from-bot`

## Commits
- `4f262e5` feat(feature-requests): create form in UI with title/desc/photos
- `f81a614` fix(feature-requests): styled "Add photos" button replaces bare file input
- `7d59e18` fix(estimator-memory): obvious "+ New" buttons

## TODO
- Артём подтвердил, что Memory кнопки заметны. По Feature Requests тест из UI ещё не делали (только curl smoke на `/from-bot`).
- Связано: [[project-estimator-ai-memory]] (структура .md файлов), [[project-tsa-estimating]] (overall estimator workflow)
