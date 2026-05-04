---
name: TG Voice Chain Autoplay
description: voice-tutor — на голосовой ввод отвечать только voice (без text-эха), чтобы TG автопроигрывал цепочку voice-сообщений в наушниках/CarPlay
type: feedback
originSessionId: c0b57883-23e3-4a7e-a819-07a5b403c8f9
---
В voice-tutor (`@AISmartFriendBot`, `/root/voice-tutor`) UX оптимизирован под "руки заняты, наушники в ушах". Telegram chain-plays подряд идущие voice-сообщения автоматически — но любой текстовый bubble между ними рвёт цепочку и заставляет тыкать кнопку.

**Правило:**
- На голосовой ввод (handle_voice) → отвечать ТОЛЬКО voice, без эха транскрипта и без текста-дубликата
- На текстовый ввод (handle_text) → voice + text (раз пишет — значит смотрит экран)
- Эхо транскрипта `🎤 ...` только под `VT_ECHO_TRANSCRIPT=1` (debug)

**Why:** Артём 2026-05-02 явно попросил «голосовой ответ автоматически после создания, меньше клацать». Это про autoplay-цепочку TG, не про API — Telegram Bot API не имеет принудительного autoplay, единственный способ — не разрывать voice-цепочку.

**How to apply:** Если будут добавляться новые типы ответов (фото, ссылки, разбивка длинных reply'ев) — для voice-input делать их silent или вообще пропускать; voice — единственный allowed message type в voice-input flow. Для text-input ограничений нет.
