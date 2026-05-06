---
name: Morning Briefing Connectors — на паузе
description: Артём хочет персональный morning briefing (Gmail+Calendar+Drive+Otter); решение отложено до ответа Тима по emails-optimization
type: project
originSessionId: 575a318b-b59b-4cda-ae63-5b8d916d9756
---
**Что:** Артём 2026-05-06 предложил добавить ему ежедневный morning briefing — sweep по Gmail / Google Calendar / Google Drive / Otter.ai (meeting transcripts). Поставлено **на паузу**: Артём идёт спрашивать Тима что тот хочет добавить в emails-optimization, после этого вернёмся к этому вопросу.

**Why:** не пересекать собственный персональный briefing с возможным расширением emails-optimization для Тима — может дешевле сделать единый стек. Артём не хочет двойной работы.

**How to apply:**
- Если Артём вернётся — предложить два пути:
  - **A. Native claude.ai** — Connectors (Gmail/Calendar/Drive, OAuth 30s) + Automations на Max плане; доставка в claude.ai/email. Otter — через MCP (Otter Pro+ API).
  - **B. VPS** — отдельный сервис `/root/morning-briefing-bot/`, Claude API + Google API + Otter API, доставка в Telegram. Стек как у emails-optimization.
- Уточняющие вопросы при возврате:
  1. Gmail/Calendar/Drive — `borysiukartem55@gmail.com` или другой аккаунт?
  2. Otter.ai план (Free / Pro / Business) — определяет API доступ.
  3. Доставка — claude.ai inbox / email / Telegram?
- Если Тим попросит расширить emails-optimization чем-то похожим (briefing по своим встречам/календарю) — рассмотреть единый сервис, который и Артёма и Тима обслуживает.
