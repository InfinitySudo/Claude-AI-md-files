---
name: Action-type identifiers — никаких имён людей в коде
description: ask_tim → ask_owner; имя в идентификаторе с маленькой буквы выглядит как ошибка в его имени
type: feedback
originSessionId: 58e3834e-1b62-4ea5-bd65-3c76fe531f55
---
Я назвал планерный action_type `ask_tim` — и эта строка случайно протекла в
TG-карточки и доку Тима. С маленькой 't' это читается как "имя Tim
испорчено". Артём поймал на ревью 2026-05-08.

**Why:** Идентификаторы в коде не должны содержать имена пользователей —
ни stylistically (lowercase ломает grammar), ни архитектурно (если
завтра тот же агент даст жене Артёма, имя становится мисфит).

**How to apply:**
- Action-type/enum/event-name идентификаторы — name-agnostic:
  `ask_owner`, `notify_user`, `confirm_with_user` — НЕ `ask_tim`,
  `notify_artem`.
- В user-facing labels (`ACTION_LABELS`, тексты карт) использовать имя с
  заглавной или нейтральное "you": `❓ Ask you`, не `ask_tim`.
- Если уже наделал — переименование лучше делать ДО первой DB-строки;
  иначе нужна миграция.
