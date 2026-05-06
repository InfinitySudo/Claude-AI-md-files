---
name: OnTime CSS variables — actual names
description: Frontend CSS-переменные TSA — НЕ пиши --tsa-fg, в проекте --tsa-text
type: feedback
originSessionId: 5d50c081-8779-4229-bd8c-a5ee134586c9
---
В `src/index.css` определены: `--tsa-primary`, `--tsa-primary-dark`, `--tsa-bg`, `--tsa-surface`, `--tsa-border`, `--tsa-text`, `--tsa-muted`. **Нет** `--tsa-fg`.

`text-[var(--tsa-fg)]` "работает" по случайности: невалидный цвет → CSS падает на inherited (черный body color). Но `bg-[var(--tsa-fg)]` = прозрачный (нет родительского bg) → элементы становятся невидимыми (tooltips, бейджи).

**Why:** Артём 2026-05-06 сообщил что tooltip и hours-labels на DailySpendPanel невидимы; найден root cause — я ошибся именем переменной.

**How to apply:**
- Текст: `text-[var(--tsa-text)]` или Tailwind-классы `text-slate-900` / `text-black`
- Тёмные backgrounds для tooltip/badge: `bg-slate-900` (явный hex), не arbitrary CSS-var
- Перед добавлением arbitrary value `[var(--tsa-X)]` — проверь что переменная есть в `index.css :root`
- Существующие места в коде с `text-[var(--tsa-fg)]` (`InvoiceInbox.jsx:444`, `ServicePage.jsx:639`, `DeliveriesPage.jsx:316`) — legacy, работают только потому что текст наследует от body
