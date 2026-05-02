---
name: Claude Telegram Bot repo
description: Personal "Bot для общения с тобой" — /root/claude-telegram-bot, pushes to Claude-Telegram-Bot repo (not OpenClaw-v3)
type: project
originSessionId: 5365f0ed-2b91-4f6b-90a2-8a6d90dc3dcd
---
Репо: `/root/claude-telegram-bot` → `github.com/InfinitySudo/Claude-Telegram-Bot` (private)

**Why:** До 17-04-2026 этот бот жил как 1 initial commit в `OpenClaw-v3` репо и дрейфовал локально без версионирования. Отдельный репо `Claude-Telegram-Bot` создан, remote переключён, состояние Apr-12 залито.

**How to apply:**
- Systemd unit: `claude-telegram-bot.service` (running), WorkingDirectory `/root/claude-telegram-bot`, запускает `claude_bot.py` напрямую (не из venv).
- Код — один файл `claude_bot.py` ~1900 строк: Telegram + OpenAI (Whisper STT + TTS onyx) + Anthropic SDK через OAuth (`/root/.claude/.credentials.json`) + smart router (Haiku/Sonnet/Opus) + tool use (execute_command/read_file/write_file/list_directory/http_request) + vision.
- Telegram token и OpenAI ключ — в systemd unit через `Environment=…`, НЕ в коде (кроме hardcoded fallback для TG token — OK в приватном репо).
- Из этой структуры клонирован CELPIP-бот (`/root/English-Teacher-CELPIP`), но с вырезанными trading-tools и CELPIP-слоем.
- Когда правишь claude_bot.py — **коммить и пуши** в Claude-Telegram-Bot, не в OpenClaw-v3.
