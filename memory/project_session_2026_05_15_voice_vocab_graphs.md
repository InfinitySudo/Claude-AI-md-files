---
name: session-2026-05-15-voice-vocab-graphs
description: 2026-05-14/15 ночная сессия — Silero RU TTS на ПК1 + voice-tutor на OpenAI nova + wife/son tutor vocab/word-lookup 28s→1.3s + OnTime Graph crash fix + Graphs Hub
metadata: 
  node_type: memory
  type: project
  originSessionId: e9dcb2ba-2eda-4ca5-9ed1-45dbffdbe1de
---

Большая ночная сессия 14→15 мая 2026 через @AISmartFriendBot и @DexClaudCodAIBot.
Несколько связанных треков, общая нить — TTS-голоса и UX-производительность для родственников.

## 1. Silero RU TTS на ПК1 (живёт, default = baya)
- `C:\Users\tkach\silero-tts\main.py` :8005, OpenAI-compatible. SchedTask `silero-tts-server` с AtBoot.
- Главная грабля: Silero v4_ru **глотает голые цифры**. `_expand_numbers()` через `num2words(lang="ru")` ОБЯЗАТЕЛЕН (`109543` → «сто девять тысяч пятьсот сорок три», `$100` → «сто долларов», `25%` → «двадцать пять процентов», `2.5` → «два целых пять»). Без него аудио обрывается.
- 5 голосов: `aidar baya kseniya xenia eugene`. Артём слушал семплы через `https://voice.constantwrestling.cloud/static/silero_samples/v3_*.mp3` — выбрал `baya` как default Silero. Закреплено в `start.bat`: `set SILERO_DEFAULT_VOICE=baya` (env-driven; `nova` маппится в DEFAULT_SPEAKER).
- ⚠ taskkill по `python.exe` или `commandline like '%silero%'` НЕ матчит — `main.py` относительный путь. Использовать `commandline like '%main.py%'` или останавливать через `schtasks /End /TN silero-tts-server`.
- Логи кастомные с текстом запроса в `stderr.log` (uvicorn перенаправляет logging.StreamHandler в stderr).
- **Подробности** в [[project_pc1_homelab_active]].

## 2. voice-tutor: финально перешёл на OpenAI nova HD для русского
- Артём сравнил Silero baya vs OpenAI nova → выбрал nova за «теплоту» (Silero дикторски-сухой).
- `VT_RU_TTS_BACKEND=openai` (default) роутит RU прямо в cloud, минуя Silero. `silero` как fallback.
- `VT_OPENAI_TTS_MODEL=tts-1-hd` (default) — заметно теплее tts-1.
- ⚠ **Грабля DeepSeek base_url** — OPENAI_BASE_URL=`...deepseek...` в .env уводит cloud-вызов TTS на DeepSeek (404). Раньше пряталось т.к. RU всегда шёл в Silero. Починил через явный `OpenAI(api_key=…, base_url="https://api.openai.com/v1")` для openai_client + stt_openai_client. См. [[feedback_tutor_tts_wiring]].
- CLI smoke-test gotcha: shell имеет глобальный `OPENAI_API_KEY=sk-5466e...` (старый/чужой), не `.env`-овский `sk-proj-…`. Перед `python -c …` ВСЕГДА `set -a; source .env; set +a` иначе 401.

## 3. wife-english-tutor: vocab + word lookup 28s → 1.3s
**Жена жаловалась на «очень долгую загрузку нового слова». Найдены 3 источника:**
1. `vocab.py::stats()` дёргал `list_due(limit=999)` — full scan + Python `datetime.fromisoformat()` per row на каждом `/api/vocab`. Пере-fixed на `julianday('now') - julianday(learned_at) >= N` в SQL. Bench 195 слов: 4× full scans → 2.1ms median.
2. `app.js gradeCard` ждал POST `/api/vocab/grade` ДО показа next card. Optimistic UI — advance мгновенно, grade в фоне (`.catch(()=>{})`).
3. `reading.py lookup_word` (тап на слово в Books): cache miss = 28s. PC1 Ollama (qwen2.5:7b, 8s timeout + 6s ответ на JSON-prompt) → Claude Haiku → OpenAI TTS — всё серийно. Cut Ollama (Claude Haiku 0.9s на той же задаче), TTS в `threading.Thread(daemon=True)`. Cache miss теперь 1.3s. Frontend `read.html`: Pronounce always shown + lazy re-fetch on click + silent preload через 2s.

**[[feedback_wet_word_lookup_slow]] записан отдельно** — паттерн "Ollama для JSON-задач — НЕ silver bullet".

## 4. son-french-tutor: zerkalit те же фиксы
Зеркалил все 3 фикса — vocab.py, app.js gradeCard, reading.py lookup_word, read.html lazy audio. Бенчи идентичные.

## 5. wife-english-tutor: avatar 33vh
До: `#avatar-stage` 50vh — занимал пол-экрана. После: 33vh + min-height 200px + `object-position: center 32%` (картинки 1024×1024, лицо/глаза на ~32% от верха). Хост — `teacher1.constantwrestling.cloud` (НЕ wife-tutor.* как я сначала подумал).

## 6. OnTime Graph: «правая сторона пустая» — cytoscape crashed
- Артём смотрел `https://teacher1.constantwrestling.cloud/ontime-graph/`. Sidebar заполнялся (146/1241), а canvas был пустой.
- Корень: `Can not create edge ... with nonexistant target material:21`. **598 строк** в `project_materials` ссылались на `canonical_id`, которых нет в `canonical_materials` (data drift в OnTime БД). Builder выводил edge но не node для них; cytoscape отказывался строить весь граф.
- Fix в 2 местах:
  - `tools/ontime_graph/build_graph.py`: после edges-loop фильтр `[e for e in edges if e['source'] in valid_ids and e['target'] in valid_ids]`.
  - **Все 5** `/var/www/{ontime,memory,projects,trading,tutor}-graph/graph.html`: defensive `Set` с node-id и skip orphan edges перед `elements.push`. Любой будущий schema drift просто `console.warn`, не белый экран.
- Также `graph.html` rewritten как responsive (drawer на ≤900px) + safer init (try/catch вокруг fetch+cytoscape, status indicator внизу слева, `100dvh` для iOS Safari, ResizeObserver/orientationchange re-fit).
- После cleanup OnTime: 144 nodes / 643 edges. Vendors отвалились — все их edges были orphan'ами. **TODO**: чистка OnTime DB чтобы вернуть vendors. Артёму сказал но он не просил chinit сразу.

## 7. Graphs Hub
**🔗 https://teacher1.constantwrestling.cloud/graphs/**
- `/var/www/graphs-hub/index.html` (синхронен с `graph-system/tools/graphs_hub/`).
- 5 pills (ontime/trading/tutor/projects/memory) переключают iframe.
- URL hash deep-link: `/graphs/#tutor` сразу открывает Tutor.
- Hardcoded stats в pills. Текущие: ontime 144/643, trading 211/678, tutor 412/422, projects 248/458, memory 283/106.
- Nginx route добавлен в `/etc/nginx/sites-available/wife-english-tutor`: `location = /graphs/ { alias /var/www/graphs-hub/; try_files /index.html =404; }` + 301 без слеша.
- ⚠ Nginx config — НЕ в git. См. [[project_unversioned_prod_state]]. Если потеряется, восстанавливать вручную.

## 8. Что НЕ сделано / висит
- **OnTime DB cleanup**: 598 orphan FKs в `project_materials` — фактический ремонт данных, не графа. Нужно `DELETE FROM project_materials WHERE canonical_id NOT IN (SELECT id FROM canonical_materials)` ИЛИ восстановить недостающие canonical_materials. Артёму сказано, на потом.
- **Graphs Hub stats refresh**: пилюли с числами hardcoded. JSON у каждого графа уже содержит `stats.nodes/edges` — можно сделать async fetch при загрузке hub'а. Не приоритет.
- **DexClaud скрин не сохранился**: фото от Артёма в @DexClaudCodAIBot уходят в `claude-telegram-bot::handle_photo` → temp file → `os.unlink`. Чтоб сохранить — caption начинается с `save:<name>`, файл ляжет в `/root/incoming/<name>.jpg`. Артёму это объяснено.

## Коммиты этой сессии
- `voice-tutor@7bc7378`: tts route Russian to OpenAI nova HD; explicit base_url avoids DeepSeek trap
- `wife-english-tutor@ab3a8f3`: ui: avatar takes top third (33vh)
- `wife-english-tutor@5977c55`: perf: vocab modal + word lookup ~30s → ~1.3s
- `son-french-tutor@7eb3839`: perf: mirror wife-english-tutor vocab + word-lookup speedup
- `graph-system@c252f5b`: graph: orphan-edge safety net + ontime builder dropped 598 stale FKs
- `graph-system@9b6deee`: add: graphs-hub — single landing page

(ПК1 silero-tts/start.bat правки — НЕ в git, см. [[project_pc1_homelab_active]] про `SILERO_DEFAULT_VOICE=baya`.)
