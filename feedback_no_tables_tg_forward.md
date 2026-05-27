---
name: No tables in TG-forward content
description: Markdown tables render as garbled text when forwarded in Telegram; use bullet lists in any doc Artem will copy/paste to Tim or other clients
type: feedback
originSessionId: 58e3834e-1b62-4ea5-bd65-3c76fe531f55
---
Markdown `| col | col |` tables render fine on GitHub but break when Artem
copies/pastes/forwards the text into a Telegram chat (TG mobile renders
them as one ugly run-on line).

**Why:** Artem пересылает Тиму intro-документы напрямую как сообщение в
TG, не через бота. Артём явно сказал: "tablici ploho otobrajautsya v TG
kogda ya peresilau Timu" (2026-05-08).

**How to apply:**
- В `docs/tim_*.md` (любые документы под пересылку) — только bullet lists.
- В `docs/tim_user_guide.md` — таблицы OK, потому что `app/help_text.py::_convert_table()` конвертит их в bullets перед рендером в `/help`. Но если файл будет также копироваться вручную, всё равно лучше bullets.
- При написании любого "пришли это Тиму/клиенту"-сообщения в чат — ZERO markdown tables. Bullets, numbered lists, code-blocks — да; pipe-tables — нет.
