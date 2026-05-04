---
name: React hooks must come before early return
description: Adding useMemo/useState/useEffect AFTER `if (!task) return null` blanks the modal — Rules of Hooks violation
type: feedback
originSessionId: a86c82dd-a6d1-4564-8fcb-d5685124b663
---
В OnTime (и любом React-проекте) добавлять `useMemo`, `useState`,
`useEffect` нужно **до** любого `if (...) return null` / условного
early-return. Иначе на первом рендере (когда условие true) хук не
вызывается, на втором (когда данные подгрузились) — вызывается. React
бросает "Rendered more hooks than expected", модалка уходит в blank
screen, а в журнале backend ничего нет (API отвечает 200, всё ломается
в браузере).

Случилось 2026-04-30 в `ServicePage.jsx` (TaskDetail): новый `useMemo`
для `mentionableByRole` оказался после `if (!task) return null`. Артём
получил пустой экран при клике на любую service-задачу.

**Why:** React требует чтобы порядок и количество хуков были
идентичны на каждом рендере. Early-return до хука это нарушает.

**How to apply:**
- Перед написанием/просмотром хука глазами проверь, нет ли выше него
  условного `return` в том же компоненте.
- Если хук зависит от данных, проверяемых в early-return, всё равно
  ставь хук выше — внутри хука обработай отсутствующее состояние
  (e.g. `useMemo(() => data ? ... : null, [data])`).
- Если правишь чужой компонент с уже существующим early-return и
  добавляешь хук, **перенеси хук выше early-return сразу**, не
  откладывай.
- API-логи на backend = 200 OK + blank screen у пользователя — почти
  наверняка hooks-order баг или JSX exception, а не сеть.
