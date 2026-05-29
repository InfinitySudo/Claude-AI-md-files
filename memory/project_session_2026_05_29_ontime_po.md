---
name: session-2026-05-29-ontime-po-push-june-work-plan
description: Late commit 9747361 of OnTime PO workflow (attachments/SMTP/rich fields) + June 2026 Work Plan PDFs (RU/EN) generated from tsa.db
metadata: 
  node_type: memory
  type: project
  originSessionId: ac8e0962-7b94-4c22-ae83-6f0318c21871
---

Сессия 2026-05-29.

## OnTime — запоздалый commit/push (9747361 на main)
Работа нескольких прошлых сессий лежала без commit. Запушено одним коммитом: полный
PO-workflow — attachments, реальный SMTP send PO PDF вендору, ~11 новых колонок PO
(order_type/po_mode/terms/need_by_window/cc/billing/…), next-number preview, vendor-emails,
mark-all-delivered / clear materials; frontend ProcurementPage/OrdersTab/ProjectForm/
ServicePage/AddressAutocomplete/ShiftPage/api-client. Детали в [[project-tsa-procurement]].
- Закоммичены ТОЛЬКО 8 source-файлов явным `git add`; `.bak`, `tsa.db.bak_pwd_reset_*`
  (underscore — gitignore ловит только `tsa.db.bak-*` с дефисом!) и `June_2026_Work_Plan.pdf`
  оставлены untracked. `npm run build` прошёл до push (правило CLAUDE.md). dist/ не в git.

## June 2026 Work Plan (PDF для «деревянных коллег», не в git)
Сгенерировал план расстановки бригад из реальных данных `backend/tsa.db`:
- **Workers now** считать по `daily_reports`, НЕ по `work_sessions` (сессии двойн-считают —
  человек на B8+B9 за неделю → 2 раза, давало ложные 41). Правило: 1 работник = его последний
  отчёт за 14д (отчёт=истина, один объект/день). Сумма сверяется к ростеру 38
  (32 монтажника + 6 рабочих форманов; 7-й форман 0ч надзор).
- **Сценарии MIN/AVG/MAX** (Артём задал): MIN 8ч×5; AVG 9ч Пн–Чт+8ч Пт = 88ч/2нед (ровно порог,
  0 овертайма); MAX +8ч Сб = 104ч/2нед (16ч OT ×1.5). Overtime >88ч за 2-нед payroll = ×1.5.
  Payroll на полной ставке 38.52 $/ч: $257,622 / $283,969 / $354,230.
- Главный вывод: ограничение — не люди, а готовность объектов (обязательные июньские дедлайны
  = всего 1,172ч, длинный бэклог 9,026ч нельзя сжать в месяц; Hillhurst = 4-мес работа).
- Итог: 2 PDF (RU+EN, по 2 стр.) через weasyprint + DejaVu Sans, отправлены в TG
  @DexClaudCodAIBot (token/owner-id хардкод-дефолты в `/root/claude-telegram-bot/claude_bot.py`,
  owner 504609639). Исходники: `/root/crew_plan_june*.html`.
