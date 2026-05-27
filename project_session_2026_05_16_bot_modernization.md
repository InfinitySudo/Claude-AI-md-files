---
name: session-2026-05-16-bot-modernization
description: "Session checkpoint 2026-05-16 — gerchik setup-explainer, wife-english-tutor books/vocab fixes, claude-telegram-bot plan-first + Opus-only modernization"
metadata: 
  node_type: memory
  type: project
  originSessionId: f70afc19-ea49-486a-8c9e-b332332d417d
---

# Session 2026-05-16 — три проекта, 12 коммитов

## 1. gerchik-trading-agent — setup-explainer

Артём вчера прервал сессию когда добавляли инструкции в TG бота. Закончил:

- В шаге `setup` wizard'а @GTE_AI_TradingBot новая кнопка `ℹ️ Что это? — объяснение`
- Открывает экран с ASCII-схемами для 4 setup-типов (Lvl-retest / BO-retest / FBO / Range-edge) + иерархия по риску
- Длина 2297/4096 chars, в одно TG-сообщение
- Возврат через существующий `back_setup` handler

**Коммит:** `1035d46` `feat(signals_bot): inline setup-type explainer in wizard`

## 2. gerchik trading проверка sid 19/20/21

Артём дважды посылал XPL SHORT @ 0.0838. Ни один не дошёл до биржи:

| sid | symbol | result |
|---|---|---|
| 19 | AIAUSDT | skipped — символ delisted на Bybit |
| 20 | XPLUSDT | expired — level breached (cur 0.0859 > SL 0.0842) |
| 21 | XLPUSDT | active, executor крутит "Symbol Is Invalid" каждые 30с — typo, на Bybit нет XLP |

Артём ничего не закоммитил по этому — sid=21 остался висеть. **Открытый вопрос:** что делать с sid=21 (rename в XPL = expired сразу, поднять level вручную, или skip).

**Level_breached guard в copy_executor:** SL = level ± 0.5% (Gerchik 1R rule). Если current_price уже за SL — auto-expire. Артём спорил с логикой, я объяснил: SL зона уже простреляна → R:R испорчено. Не закрыто решение.

## 3. wife-english-tutor — 3 коммита

Liliya жаловалась: «Books не работает», потом «Cannot read properties of undefined (reading '13')», потом «Could not load vocab: 404».

Корень — фронт написан с endpoints которых не было на бэке (а в son-french-tutor те же endpoints были давно). Реализация:

| Коммит | Что |
|---|---|
| `530a5b0` | `/read` + 7 books endpoints (вкладка Books не открывалась) |
| `514a4aa` | `/api/books` возвращает `progress: {book_id: last_chapter}` + defensive frontend `data.progress \|\| {}` (id=13 Speckled Band крашил) |
| `b950b8d` | `/api/vocab`, `/api/vocab/grade`, `/api/pronounce` |
| `598e333` | 🔊 listen button на каждом vocab-слове (one retry after 1.5s pattern) |
| `995ae70` | bump cache-bust `?v=20260516b` в index.html |

Bot/handlers были давно готовы в `bot/reading.py`, `bot/vocab.py`, `bot/pronounce.py`. Просто никогда не зарегистрировали в `web/app.py`. son-french-tutor — reference impl.

**Память:** `[[wet-frontend-backend-drift]]` — sweep grep frontend vs backend перед debugging.

## 4. claude-telegram-bot (@DexClaudCodAIBot) — главная модернизация

Артём попросил: «давай научим бота составлять план перед задачей + показывать прогресс в TG как в Claude Code status-line». Прислал картинку: progress bar в стиле `▰▰▰▰▰▰▰▱▱▱▱▱ 56% · 3m 26s · ↑2.9k tokens`.

### Архитектурные изменения

**1. Новые tools** в `CLAUDE_TOOLS`:
- `create_plan(title, steps)` — ОБЯЗАТЕЛЬНО первым для multi-step. Создаёт `task_state[user_id]`.
- `update_progress(current_step)` — ПЕРЕД каждым новым шагом. 0-indexed.

**2. Live progress UI** — `_render_progress(state)` рендерит:
```
🔧 *Title*
▰▰▰▰▰▰▰▱▱▱▱▱ 67%  ·  2m 14s  ·  ↑8.4k
[✓] (1/6) ...
[▶] (2/6) ...
[○] (3/6) ...
```
Edit-in-place один `msg_id`, не спам.

**3. Auto-status fallback** — даже если бот забыл `create_plan`, status_callback редактирует один message «🔧 Работаю... N tool calls · 2m 14s» вместо спама. Подсказка в самом сообщении «попроси план».

**4. Token tracking** — `_accumulate_usage(response)` после каждого `_call_api`.

**5. Финализатор** — `finalize_task_progress()` после `ask_claude` дотягивает прогресс до 100%, чистит `task_state` и `auto_status`. `/clear` также чистит.

### Routing changes

**Opus 4.7 ЖЁСТКО для code/bug/fix:**
- `MODEL_OPUS = "claude-opus-4-7"` (bump с 4-6)
- `CODE_PATTERNS` расширен: латиница (`ne rabotaet`, `pochini`, `dobav`), project names (`voice-tutor`, `wife-english-tutor`, `gerchik`, ...), paths (`/root/`, `.py`, `.service`), HTTP errors (4xx/5xx, OAuth, CORS)
- Страховка: длина >120 chars → авто code_request = True
- `forced_model` (`/sonnet`, `/haiku`) **игнорируется** для code/trading — overrride на Opus
- Fallback chain отключён для code/trading: `models_to_try = [primary_model]`

### Retry-after на rate-limit

`_call_with_retry(model, messages)` — для opus_only до 3 попыток с retry-after из заголовка ответа (capped 60s). Status callback показывает `⏳ Opus rate-limit · жду 15s · ретрай 2/3`.

Если все 3 фейл → честное сообщение про общую 5h-квоту Claude Code (Opus+Sonnet+Haiku делят квоту → fallback бесполезен).

### SYSTEM_PROMPT

Правила №1 (план) и №2 (Opus 4.7) подняты в самый верх, не закопаны.

### Коммиты (6 шт., все запушены 2026-05-16 23:37)

```
bfadc17  Plan-first workflow + Opus-4.7-only + live progress UI
e600f8e  CODE_PATTERNS латиница + auto-status fallback + plan rule to top
e7dff50  Auto-retry на Opus rate-limit с retry-after
cb6712b  (черновик /sonnet escape — частично откатили)
e90ef83  (промежуточный)
3400f58  ← Revert /sonnet escape: общая квота делает fallback бесполезным
```

Pushed: `e2d0dc9..3400f58 main -> main` в `InfinitySudo/Claude-Telegram-Bot`.

### Статус тестирования

Артём в конце сессии упёрся в Claude Code 5h-квоту → все модели заблокированы → не успели протестировать live-progress на реальном запросе. Бот в проде ждёт сброса квоты.

**Когда квота отпустит** — Артём должен попробовать `prover voice tutor opyat` и увидеть:
1. Бот читает `/root/voice-tutor/CLAUDE.md`
2. Вызывает `create_plan` с 3-6 шагами
3. Live edit-in-place прогресс-бар
4. В конце все [✓] + текстовый отчёт + label `[🔥 opus]`

Если план не появится — крутить SYSTEM_PROMPT дальше.

## Open items

1. **gerchik sid=21 XLPUSDT** — висит active, executor спамит "Symbol Is Invalid". Решение не принято (rename/skip/manual fix).
2. **DexClaudCodAIBot live-progress тест** — ждёт сброса 5h-квоты Claude Code.
3. **Claude Code квота** — общая для Opus+Sonnet+Haiku на OAuth-плане; альтернатива (если будет упор регулярно) — отдельный `ANTHROPIC_API_KEY` с per-token billing.
