---
name: project-session-2026-05-28-ontime-orders
description: 2026-05-28 OnTime session — orders inline-edit + bulk PO + material_requests + PDF cyrillic + ProjectsPage search/sort + mention whitelist + estimator bot users + Artem PM
metadata: 
  node_type: memory
  type: project
  originSessionId: bb73faf2-7236-4331-be4f-672a9a8928b5
---

Сессия 2026-05-28, commit `07e0a07` (push: `7d59e18..07e0a07 main`).

## Что сделано

### 1. Siding Estimator Bot — whitelist
- `/root/siding-estimator-bot/.env`: `SIDING_BOT_ALLOWED_IDS=1096715173,821348233` — Ihor Marchenko (`director_estimator`) + Taras Borets (`estimator`).
- `siding_estimator_bot.py:42-47` — ALLOWED_IDS = {OWNER_ID} ∪ env; `owner_only` decorator проверяет членство в set.
- В OnTime users.id=89 (Taras Borets) проставлен tg_chat_id=821348233.

### 2. BOM converter (.numbers → OnTime)
- Артём прислал .numbers с колонками `Description | Est. Qty. | UOM | MPN | UPC | Unit Price | Cost Code`.
- ⚠ В исходнике колонка "Cost Code" фактически содержала *total cost*, а Unit Price была пустая. Conversion: `unit_price = total / qty`.
- Script `/tmp/bom-import/convert.py` использует `numbers-parser` + `openpyxl`. Готовый CSV/XLSX (формат `Item Name | Qty | Unit | Unit Price | SKU`) отправлен Артёму через `@TSA_EstimatorBot` (TG bot API `sendDocument`).
- OnTime ProjectForm `onUploadBom` (`src/components/ProjectForm.jsx:145-322`) парсит этот формат на лету.

### 3. ProjectsPage — поиск + сортировка
- `src/pages/ProjectsPage.jsx`: input search (name/address/foreman/type/size), select sort (Deadline/Name/Progress/Budget/Result/Foreman/Size/LastActivity) с дефолтным направлением для каждого, кнопка ↑/↓.
- Состояние в localStorage (`projects.q`, `projects.sortBy`, `projects.sortDir`).
- Иконка лупы — `left-3`, padding inline-стилем `2.25rem` чтобы перебить класс `input` (был трап слипания).

### 4. OrdersTab — inline-edit + multi-select + bulk PO
- Колонка **Price** добавлена. Inline-edit для name/price/plan-qty через `<InlineCell>` (helper компонент: click→input→onBlur/Enter save, Esc cancel). Корзина при hover для admin удаляет из BOM.
- Multi-select: чекбоксы в каждой строке + master в каждой категории + общий «Select all (N)» в sticky-панели.
- Bulk action:
  - management → «New PO from N» открывает POFormModal с массивом prefillItems (уже умел).
  - foreman → «Request N» делает N параллельных POST'ов в `request-order`.
- Кнопка «Order» в строке: management → PO modal с одним материалом; foreman → prompt qty/note → material_request.

### 5. Material requests — foreman→purchasing flow
- Backend `main.py`:
  - Таблица `material_requests` (id, project_id, material_id, qty, note, requested_by, requested_at, status, handled_by, handled_at, po_id).
  - `POST /api/projects/{pid}/materials/{mid}/request-order` — пишет запись + рассылает `notify_with_store(kind='material_request')` всем purchasing_manager + director + admin (link_url=`/projects/{pid}?tab=orders`).
  - `GET /api/projects/{pid}/material-requests?status=open` — список.
- Frontend `api.projectMaterials.requestOrder/listRequests`.

### 6. POFormModal — защита от вылета
- Артём сообщил «при создании New PO выкидывает из app» — корневую причину локализовать не успел.
- Workaround: `POErrorBoundary` (class component) оборачивает оба `<POFormModal>` — теперь крах не выкидывает на login, показывает красную плашку с message + Close.
- Backend `POST /api/log-client-error` — sink для error stack из ErrorBoundary (print в journal `ontime-api`).
- Defensive fix: `bm.available_qty.toFixed()` → `_round(Number(bm.available_qty || 0))`.

### 7. PO PDF — кириллица + дубль адреса
- `_render_po_pdf`: helper `_ensure_unicode_fonts()` регистрирует DejaVu Sans (system `/usr/share/fonts/truetype/dejavu/`) + addMapping(regular/bold). Все ParagraphStyle и TableStyle FONTNAME → `_PDF_FONT_REGULAR/_BOLD`. Раньше Helvetica не имела глифов для кириллицы → «Калгари, Альберта, Канада» → ▪▪▪.
- SHIP TO дубль: `po.delivery_address` печатается только если `_norm_addr(delivery) != _norm_addr(project)`.

### 8. @mention dropdown
- `GET /api/projects/{pid}/messages/mentionable` — теперь возвращает ВСЕХ активных company users кроме `installer` и `helper`, sorted by full_name COLLATE NOCASE, limit 200 → потом filter по q + slice(20).
- Раньше был узкий whitelist (admin/pm/vp/director/director_estimator/estimator/accountant) — не хватало purchasing/mechanic/service/delivery/office_assistant/foreman.

### 9. Artem PM учётка
- users.id=8 (`borysiukartem55@gmail.com`, был `installer`) → роль `pm`, tg_chat_id=`504609639`.
- Основная admin-учётка id=4 (`borysiukartem1990@gmail.com`) не тронута.

## Связи
- [[project-estimator-links]] — Estimator bot whitelist расширение
- [[feedback-ontime-bom-replace-trap]] — BOM upload flow
- [[project-tsa-procurement]] — POs + approval chain
- [[feedback-fastapi-route-order]] — sub-resource route shape (`/materials/{mid}/request-order` трёхсегментный — OK)
