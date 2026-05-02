---
name: solo_claude_bot infra
description: CLI в /root/solo_claude_bot для постинга в TG-каналы @solo_claude (main) и drafts. Два бота, токены в .env (chmod 600), CHAT_* нужно заполнить после создания каналов.
type: project
originSessionId: d17635cc-9fb8-4333-ba35-356494af8a39
---
**Путь:** `/root/solo_claude_bot/`. Свой venv (`.venv`), deps: `requests`, `python-dotenv`. Создан 2026-04-16.

**Боты (верифицированы через getMe):**
- `@solo_claudeBot` (id 8709028116) — публикация в публичный канал @solo_claude. Переменная `BOT_MAIN_TOKEN` в .env.
- `@SoloClaudeChernovikBot` (id 8623848438) — постинг в приватный drafts-канал. Переменная `BOT_DRAFTS_TOKEN`.

**Что нужно дозаполнить в `.env`:**
- `CHAT_MAIN` — numeric id канала @solo_claude (формат `-1001234567890`).
- `CHAT_DRAFTS` — id приватного drafts-канала.
Получать через `@userinfobot`: переслать туда любое сообщение из канала, вернёт id.

**CLI:** `./post.py drafts <file.md>` / `./post.py main <file.md>` / `./post.py test drafts|main`.
- Первая строка файла `# html` → парсится как HTML. `# plain` → plain text. Иначе — MarkdownV2 с автоэкранированием.
- Черновики хранятся в `drafts/NNN-slug.md`. Первый готовый: `drafts/001-pinned-post.md` (финальный pinned-пост).

**Workflow:** я пишу драфт → `post.py drafts` → Артём правит inline в TG → копирует финал обратно в файл → `post.py main` (вариант 1 с ручным copy-paste тоже остаётся).

**Безопасность:** `.env` chmod 600, в .gitignore. Если этот репо когда-нибудь окажется в git — проверить что .env не попал.

**How to apply:** Любой пост для @solo_claude начинается с нового файла в `drafts/`. Номер инкрементный. Команды `post.py` можно вызывать из Bash в этом же чате — в будущих разговорах просто бегу по диалогу: написал → `post.py drafts` → жду правки.
