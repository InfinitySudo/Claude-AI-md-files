---
name: No API Keys for Invoice Parsing
description: В OnTime invoice pipeline НЕ использовать Claude/OpenAI API. Только regex per-vendor parsers как сделали для Roofmart.
type: feedback
originSessionId: fe2d774e-d849-434f-9578-413ba05df8a4
---
Артём явно сказал 2026-04-28: «не хочу использовать никаких API ключей, мы с тобой уже делали эту работу с invoices для Roofmart и у нас отлично вышло, продолжаем в том же духе без API».

**Why:** Roofmart показал что regex-template подход надёжен и работает на сотни PDF без расходов и зависимостей от внешнего API. Артём не хочет платных ключей в OnTime в принципе.

**How to apply:**
- Для каждого нового vendor пишем regex parser, как `_RM_HEADER_RE/_RM_TOTAL_RE/_RM_COMBINED_RE` в `backend/invoice_parser.py`.
- Шаблоны хранятся в `vendors.parser_template`; routing через `vendor_email_domains.domain → vendor_id → parser_template`.
- PDF без шаблона → `parsed_status='unmatched'`, остаётся в Inbox для ручного review.
- Никаких `claude_parse` / `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` в этом pipeline.
- Если нужна более гибкая extraction — pdfplumber.extract_tables, header-row inference, или просто больше regex.
