---
name: feedback-wet-corrector-sonnet
description: "wife-english-tutor: reply_for_turn использует SONNET, не HAIKU; иначе модель ленится и правит 1-2 предложения из 5"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9ef7b3ce-b786-4fb4-851f-4508e0accb52
---

В `wife-english-tutor/bot/llm.py` `reply_for_turn` и `reply_for_turn_stream` дефолтом стоит `MODEL_SONNET` (не HAIKU). max_tokens=2000.

**Why:** Артём (2026-05-25) пожаловался: жена пишет 4-5 предложений, Alyona правит только 1-2 первых и забывает остальные. На HAIKU модель ленится длинные сообщения. SONNET надёжно покрывает все ошибки.

**How to apply:** Если будет нужно сэкономить — НЕ переключай корректор обратно на HAIKU. Если хочется дешевле, можно дополнительно усилить промпт-протокол в llm.py (там уже есть "ПРОТОКОЛ ПРОВЕРКИ" с пошаговым разбором), но не возвращать HAIKU без подтверждения Артёма.

Связан с [[project_progress]] (тьютор) и [[user_artem]].
