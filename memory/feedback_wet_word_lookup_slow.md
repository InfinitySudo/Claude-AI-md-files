---
name: wet-word-lookup-slow
description: "wife-english-tutor `/api/word/lookup` на cache miss занимал 28s — Ollama JSON-prompt медленнее Claude, плюс TTS блокировал ответ. Чинить через Claude-first + background TTS."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e9dcb2ba-2eda-4ca5-9ed1-45dbffdbe1de
---

В `wife-english-tutor` тап на слово в книге (`/read`) дёргает `/api/word/lookup`. До 2026-05-14 cache miss занимал **~28 секунд** — жена Лилия видела «Loading…» полминуты на каждое новое слово.

**Why:** Три серийных боттлнека в `bot/reading.py::lookup_word`:
1. `local_llm.call_local()` — PC1 Ollama qwen2.5:7b с **8s timeout** + ~6s ответа на JSON-prompt (IPA + pos + example + translation). Для JSON-задачи Ollama стабильно медленнее Claude.
2. JSON парс падал → ре-try через Claude Haiku (+1s).
3. `_synthesize_word_audio()` (OpenAI tts-1) — ещё +1s, тоже в основной цепочке.

Cache hit при этом был 1ms — то есть проблема была только в первый раз для каждого слова.

**How to apply:**
- В подобных «look up one word/phrase, return JSON» сценариях Ollama qwen2.5 на ПК1 — НЕ серебряная пуля. Claude Haiku 0.9s vs Ollama 6s на одной и той же JSON-задаче.
- TTS audio для словарных карточек **обязательно делать в фоне** (`threading.Thread(daemon=True)`), не в основном handler'е. Фронт догрузит через retry/preload — единственное аудио-нажатие в карточке отлично переживает первый «пустой» state.
- Frontend Mini App: при отображении карточки слова — **показывай Pronounce-кнопку всегда**, а не условно на `audio_b64`. Через 2s после рендера тихо ре-fetch с тем же endpoint (cache hit вернёт audio); клик до этого триггерит немедленный ре-fetch. Так UX не зависит от расписания backfill.
- Если жена/пользователь читает много слов за раз и упирается в Claude OAuth rate limit ([[feedback_oauth_rate_limits]]) — можно добавить Ollama как опциональный first-try с timeout **≤3s**, чтобы не съесть UX.
- Bench-метод: всегда вызвать `lookup_word(word, with_audio=True)` после `DELETE FROM word_lookups WHERE word_lower=?` для гарантированного cache miss, потом замерять.
