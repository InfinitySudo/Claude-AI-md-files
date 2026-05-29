---
name: project-estimating-phase-a
description: Phase A AI-assist для OnTime Estimating — 2026-05-25; siding-estimator-bot + Stack mirror + learned_rules в BOM
metadata: 
  node_type: memory
  type: project
  originSessionId: 3f969d3c-e080-450e-8ce9-fb152339bbc0
---

# Estimating Phase A — AI-assist (2026-05-25)

Цель: научить OnTime эстиматинг учитывать историю TSA из Stack CT + копить
поправки Артёма как `learned_rules`, чтобы постепенно заменить Stack.

## Что построено

**1. Siding Estimator Bot** (`/root/siding-estimator-bot/`)
- TG-бот `@TSA_EstimatorBot` (forked claude-telegram-bot, ~2200 строк)
- systemd: `siding-estimator-bot.service`
- 9 tools: search_similar_projects, get_project_bom, lookup_ontime_catalog,
  calculate_siding_bom, save_learned_rule, list_learned_rules,
  flag_for_review, list_pending_reviews, stack_sync_status
- БД общая: `/root/ontime/backend/tsa.db`

**2. Stack mirror в tsa.db** (migration 001_stack_schema.sql)
- `stack_projects` / `stack_items` / `stack_takeoffs` / `stack_assemblies` / `stack_plans`
- `stack_sync_state` — bookkeeping для дельт
- `learned_rules` — корректировки от Артёма (topic, applies_to JSON, rule_text)
- `estimator_review_queue` — эстиматы которые бот не уверен в

**3. Заполнение Stack mirror — два пути**
- `stack_sync.py` — OAuth2 client для Stack CT API (ждёт credentials, 2 раб. дня)
- `stack_import_excel.py` — ручной импорт Excel-экспортов из Stack UI (работает СЕЙЧАС)

**4. OnTime backend изменения** (`main.py`)
- `_lookup_learned_waste(...)` — консультирует learned_rules перед расчётом BOM
- `_bom_for_estimate(...)` возвращает `learned_rules_applied` массив
- GET `/api/estimates/{eid}/similar` — похожие проекты из stack_projects (siding_type + sqft±25%)
- GET `/api/stack-projects/{spid}/bom` — BOM прошлого проекта

**5. OnTime frontend** (`src/pages/EstimateDetailPage.jsx`)
- `SimilarProjectsPanel` — карточки 5 похожих с cost_per_sqft + ext-link на BOM
- Кнопка «🤖 Спросить AI» → `t.me/TSA_EstimatorBot?start=estimate_<id>`
- Deep-link обрабатывается ботом в `cmd_start`: запоминает контекст эстимата
  в `estimate_context[user_id]` (TTL 4ч), каждое сообщение оборачивается через
  `_augment_with_estimate_context`

## Что НЕ сделано (намеренно, requires apруш)

- **Vision blueprint analysis** — есть запрет `feedback_estimating_no_api`
  (Vision не предлагать для estimating). Решение по Phase B/Уровень 1 откладывается
  до накопления 20-30 эстиматов с правками Артёма.
- **Embeddings/vector search** — пока структурный фильтр (sqft+siding_type).
  Если будет мало match'ей после 50+ Stack-импортов — добавим `sqlite-vec`.
- **Customer-facing PDF reports** с брендингом TSA — Phase C (когда замещение Stack).
- **Versioning эстиматов V1/V2/V3** — Phase C.
- **Change orders / approval workflow** — Phase C.

## Стратегия замещения Stack

- Фаза A (done): параллельная работа, бот учится на корректировках
- Фаза B: hybrid — простые проекты у нас, сложные в Stack (порог: ±3% от Stack на 20+ подряд)
- Фаза C: полная замена (3-6 мес от now)

Ключевые memory:
- [[feedback-estimating-no-api]] — Vision НЕ предлагать для extraction
- [[project-tsa-estimating]] — Phase 1 (tracing UI)
- [[project-estimating-industry-rules]] — formulas + waste factors
- [[project-tsa-timeline]] — OnTime overview

## Bot token и API key

- TG: `8299228390:AAHI2UaG22ZDmN-yugHS8XX6yzQwrpc-0F0`
- Stack API: ждём ответа от apihelp@stackct.com (письмо 2026-05-25)
