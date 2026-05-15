---
name: openai-base-url-shell-override
description: "VPS shell env содержит `OPENAI_BASE_URL=https://api.deepseek.com/v1` — OpenAI Python client его подхватывает по умолчанию и роутит на DeepSeek (404 на /audio/speech, /audio/transcriptions). Лечится явным `base_url=` в коде или `unset OPENAI_BASE_URL` перед запуском."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1d54c6b-9b43-408e-bf0b-0378ebf08875
---

**Rule:** Перед использованием `from openai import OpenAI; OpenAI(api_key=...)` в любом скрипте на VPS — либо передай `base_url="https://api.openai.com/v1"` явно, либо `unset OPENAI_BASE_URL` в shell перед запуском Python.

**Why:** Артём настроил DeepSeek shim в `/etc/environment` или `~/.bashrc` для другого проекта (4BotsBybit?). Этот env var инжектится в любую interactive bash сессию. OpenAI SDK по умолчанию читает `OPENAI_BASE_URL` env первым приоритетом — выше параметров инициализации.

**Симптомы:**
- `openai.audio.speech.create(...)` → `openai.NotFoundError: Error code: 404`
- DeepSeek поддерживает chat completions но не Whisper/TTS → 404 на эти endpoints
- В коде систем который читает `.env` через `python-dotenv` — там OPENAI_API_KEY правильный, но shell env побеждает с `OPENAI_BASE_URL`

**Как поймать:**
```bash
env | grep OPENAI
# OPENAI_BASE_URL=https://api.deepseek.com/v1   ← виновник
# OPENAI_API_KEY=sk-5466eb1c... (deepseek key, не openai)
```

**Lечение в коде (надёжно):**
```python
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'],
                base_url='https://api.openai.com/v1')  # ← явно
```

**Lечение в shell (для one-off скриптов):**
```bash
unset OPENAI_BASE_URL OPENAI_API_KEY OPENAI_MODEL
python script.py
```

**Сервисы под systemd:** обычно не пострадают потому что systemd unit не наследует interactive shell env, но если EnvironmentFile=/etc/environment добавлен — пересечётся. Проверь `systemctl show <svc> | grep Environment`.

How to apply: каждый раз когда видишь `404` на OpenAI endpoint в новой сессии — это первая гипотеза. До чтения логов, до проверки credentials.
