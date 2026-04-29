---
name: OnTime Archive = junk only, не для done
description: Archive в OnTime означает мусор/cancelled/тест, а не "спрятать завершённый проект"
type: feedback
originSessionId: d0e796b4-3e9c-410b-905b-c8241cbc6fdf
---
Архивирование в OnTime НЕ для скрытия done-проектов — это для мусора (тестовые, cancelled, дубликаты, ошибки).

**Why:** 2026-04-29 Артём массово архивировал 47 завершённых проектов чтобы очистить главную страницу, не зная что dashboard YTD/monthly/working_days включали архивные данные (фильтра по archived не было). Active-projects card же фильтрует archived → inconsistency: счётчик 14 active, но YTD-деньги/часы считают 47 архивных + active. После разархивации и фикса фильтров всё стало консистентно.

**How to apply:**
- **Done-проекты прячутся через UI**: ProjectsPage default 'all' filter показывает всё кроме `status='done'`. Done доступны через chip 'Done'. Не архивировать done для очистки экрана.
- **Архив = реальный мусор**. Тесты, cancelled, дубликаты — архивировать. Завершённые с убытком/прибылью НЕ архивировать.
- **Dashboard `_dashboard_period_totals`, `_dashboard_monthly_breakdown`, `_dashboard_year_summary.working_days_ytd`** все фильтруют `archived=0` (фикс 2026-04-29). Если добавляешь новый агрегат — копируй фильтр `(p.archived IS NULL OR p.archived = 0)`.
- **Главная для foreman**: 26 active/overdue/planned карточек, не 62. Done скрыт, archived (если есть) скрыт.
