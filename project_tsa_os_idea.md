---
name: TSA OS — Unified Company Platform (on hold)
description: Idea paused 2026-04-16. Build own company management system on top of OnTime core, replacing ClickUp + Django admin + Telegram+Sheets; keep STACK and Kojo as satellites. Return to when Artem revisits.
type: project
originSessionId: d17635cc-9fb8-4333-ba35-356494af8a39
---
**Статус:** Идея обсуждалась 2026-04-16, отложена. Артём попросил запомнить и вернуться позже.

**Исходный контекст (стек TSA на момент разговора):**
- STACK — estimating (SaaS, закрытый)
- ClickUp — info storage, задачи, доки (SaaS)
- Kojo — BOM + закупка у поставщиков (SaaS)
- Telegram-бот + Excel/Sheets — подсчёт выполненных работ вручную
- Django admin panel — зарплаты, сотрудники, бюджеты (не на этом VPS, у Артёма/бухгалтера)
- **OnTime** (наш, /root/ontime) — GPS time-tracking, смены, проекты, foreman scoring

**Команда:** бухгалтер, VP of construction, 2 PM, 7 foreman, 40–50 работников.

**Боль:** 5 источников правды, ручной копипаст между ними. Нет связи estimate→факт, часы→зарплата, BOM заказ→BOM расход.

**Рекомендованная стратегия (Вариант B «Hub + connectors»):**
OnTime становится ядром («TSA OS»). STACK и Kojo остаются — тянем их данные через API/импорт. ClickUp и Django admin поэтапно закрываем, функции переезжают в хаб. Telegram остаётся интерфейсом для работников. AI-агенты сверху.

**Roadmap (4 фазы, 6–8 мес суммарно в вечернем темпе):**
1. **Payroll bridge + Budget + STACK import** (1–1.5 мес) — самое болезненное сейчас, максимум отдачи.
2. **Materials loop + Kojo sync + первые AI агенты** (Estimate sanity, Material anomaly).
3. **ClickUp replacement** — Docs/Tasks/Gantt/CRM light в хабе.
4. **AI agents layer** — Foreman assistant (Telegram+voice), VP weekly summary, Payroll anomaly, Predictive reorder.

**Economics:** текущий SaaS ~$500–1500/мес → после ~$100–300/мес (infra + Claude API $50–200). Окупается за месяцы.

**Риски:** я bottleneck; VPS нужно апгрейдить (8GB/4CPU ~$30/мес); зависимость от STACK/Kojo API.

**Открытые вопросы (блокирующие старт):**
1. Доступ к Django admin (модели Payroll) — скрины/доступ.
2. STACK API — есть или только PDF/CSV?
3. Kojo API — есть или scraping?
4. Приоритет: Payroll bridge предложен как Фаза 1, но Артём не подтверждал.

**How to apply:** Если Артём возвращается к теме — начать с этих 4 вопросов, не с кода. Без ответа на 1 и 4 нельзя проектировать Payroll module.
