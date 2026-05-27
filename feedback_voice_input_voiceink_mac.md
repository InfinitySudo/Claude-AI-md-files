---
name: voice-input-voiceink-on-mac
description: "Артём на macOS использует VoiceInk (local Whisper) для голосового ввода в SSH-сессию с VPS — не путать с VoiceLine (cloud, требует API key)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f806231e-a972-4dc0-bd04-e777e5f8a467
---

## Setup

Артём использует Mac → SSH в VPS (root@187.77.148.44) → `claude` CLI. Голосовой ввод **локально на маке** через VoiceInk; текст через SSH автоматически уходит на VPS как обычный keystroke.

- **App**: VoiceInk (open-source, https://github.com/Beingpax/VoiceInk/releases/latest)
- **НЕ VoiceLine** (другое приложение, cloud-based, требует OpenAI API key)
- **Whisper модель**: large-v3 turbo (~1.5 GB, локально на маке)
- **Hotkey**: push-to-talk, удерживать ⌥-Right (Right Option). Не Cmd — слишком много конфликтов.
- **Permissions**: System Settings → Privacy & Security → Microphone + Accessibility (для авто-paste в фокус)
- **Language**: Auto-detect (RU/EN mix работает)

## Workflow

1. iTerm2/Terminal на маке открыт, SSH в VPS, `claude` запущен
2. Кликни в окно где курсор `>`
3. Удерживай hotkey → говори → отпусти
4. Whisper API call (локальный) → транскрипт → auto-paste в фокус
5. Enter

VPS ничего знать не должен — Whisper целиком локальный, SSH передаёт keystrokes.

## SSH alias

`~/.ssh/config` на маке (Артём установил 2026-05-16):

```
Host vps
    HostName 187.77.148.44
    User root
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
```

SSH ключ artem-mac (ed25519, `AAAAC3...artem-mac`) в `/root/.ssh/authorized_keys` на VPS, отдельной строкой от старого Hostinger-ключа.

## Что НЕ работает

- Cmd как hotkey — конфликты с системой (Cmd+C, Cmd+V, Cmd+Tab). Использовать Right Option / Right Cmd / Fn / Caps Lock (remapped).
- VoiceLine — требует OpenAI/Groq API key, cloud-based. Артём ставил по ошибке, удалил.
- VoiceInk без Accessibility permission — текст только в clipboard, не auto-paste.
- `.env` на VPS имеет `OPENAI_API_KEY` пустым — это для voice-tutor, не для VoiceInk.

## PC1/PC2 в Tailscale (для справки)

- `art` 100.73.22.1 (Windows, far ping ~866ms) — PC1, user `Atrem Borisuk` (с пробелом), SSH **не настроен** для root@vps-trading ключа
- `desktop-f836b96` 100.99.211.123 (Windows, ~445ms) — PC2, user `Tkach`, SSH **доступен** для root@vps-trading. На PC2 живёт partial klines copy `C:\Users\tkach\ga_gpu\klines` (532 файла, 1.22 GB — НЕ полная резервная копия 53 GB VPS-klines).

## Связано

- [[project-voice-tutor]] — TG voice tutor, OpenAI Whisper API
- [[feedback-tutor-tts-wiring]] — TTS chain PC1→PC2→OpenAI
- [[project-gpu-homelab-plan]] — PC1 ACTIVE with Ollama, future Whisper hosting
