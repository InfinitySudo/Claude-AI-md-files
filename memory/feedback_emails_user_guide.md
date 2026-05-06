---
name: Emails — keep user guide in sync with features
description: При добавлении любой новой фичи в emails-optimization обновлять docs/tim_user_guide.md
type: feedback
originSessionId: 5508f2bd-1413-4e70-82bf-a9b87d69e0aa
---
**Правило:** Каждый раз при добавлении новой фичи / команды / кнопки в `emails-optimization` нужно правкой в `docs/tim_user_guide.md` отразить это для Тима. Бот сам перечитывает файл при `/help`, поэтому отдельный пуш в чат не нужен — но без правки гайда Тим не узнает.

**Why:** Артём 2026-05-06: "обновляй [гайд] по мере появления новых фич". Гайд встроен в бота как `/help`, рендерится из `docs/tim_user_guide.md` через `app/help_text.py`. Если гайд устареет — Тим будет видеть несуществующие фичи или пропускать новые.

**How to apply:**
- При коммите Stage 5–9 (delegate forward, project tags, urgent subcategories, morning digest, follow-up tracker) — обязательно правка `tim_user_guide.md` в том же коммите
- Структура гайда: 12 секций, разделённых `---`, рендерятся в отдельные TG-сообщения. Не использовать HTML-теги в md (помечается `<` `>` парсером — пиши на чистом markdown)
- Поддерживаются: # / ## / ### → `<b>`, `**bold**`, `*italic*`, `` `code` ``, ```` ``` ````, GFM-таблицы (конвертируются в bullets), `[link](url)`
- Если фича сильно меняет UX — обновить и `tim_user_guide.md`, и `BotCommand` список в `_set_commands` в bot.py
- Roadmap-секция в конце гайда ("What's coming next") — переезжать пункты из неё в основные разделы по мере реализации
