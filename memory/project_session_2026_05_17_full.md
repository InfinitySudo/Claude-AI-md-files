---
name: session-2026-05-17-full
description: "Большая мульти-проектная сессия 2026-05-17 — strict-rules hook, mobile-app фиксы, trading config, Insights tab, Telethon listener scaffold"
metadata: 
  node_type: memory
  type: project
  originSessionId: 52cdecb9-174f-4000-b1f8-e17b8d341e9b
---

Session 2026-05-17 — длинный день, 5+ часов работы, 30+ коммитов в 5 репо. Ключевые блоки:

## 1. Strict-rules harness setup
- Создан UserPromptSubmit hook `~/.claude/settings.json` который инжектит правила из `~/.claude/hooks/strict_plan_rules.md` в каждый prompt.
- 7 правил: PLAN FIRST (TaskCreate перед работой), молчание между шагами, прогресс-бар обязателен, вопросы только в крайних случаях, финальный summary, правильная директория, русский кириллицей.
- Параллельно сделано аналогичное для `@DexClaudCodAIBot` (`/root/claude-telegram-bot`) — в SYSTEM_PROMPT добавлены правила №3 (no chatter), №4 (questions last resort), №5 (do more than asked), №6 (right dir first), №7 (UI commands literally).
- Связано: [[strict-plan-rules]]

## 2. Mobile app фиксы (son-french-tutor + wife-english-tutor)
- 🔊 кнопка прослушки слов: на vocab card + в All-words list. Backend padding `" {word}. "` + frontend silent-WAV warmup + blob URL + per-word cache для cold-start. Endpoints на PK1 Kokoro first, OpenAI fallback (для wife). Для son — OpenAI only (PK1 English-only, не работает для French).
- Аватар Sophie: размер/стиль приведён к wife-english-tutor (33vh panoramic), back+Close кнопки = drawer-btn стиль, hover/active фиолетовый, dark-mode контраст через `var(--surface)`.
- Reading тaб: ← back всегда виден (на root → главное меню), Close внизу, /v2→/ навигация, баннеры категорий из wife скопированы в son (CATEGORY_META + bookCard + coverGradient).
- Modal dialogs (vocab/progress/mistakes): кнопка ← back в header.
- 🚨 Bug: `const _vocabAudioCache` дублировал прежний для playVocabWord — SyntaxError ломал весь app.js wife → все кнопки мертвы. Fix: переименовал на `_vocabCardAudioCache` + null-guards.
- Security incident: `git add -A` в son подцепил `.env.bak_*` + `style.css.backup` → push в публичный репо. Файлы удалены из HEAD + gitignored. Ключи (OPENAI + WET_TG_TOKEN) ротированы Артёмом, обновлены в 4 .env (wife, son, voice-tutor, emails-optimization), 9 сервисов рестартнуты.

## 3. Trading: фильтры, fees, ML, Insights
- **max_order_size 100→200** ($, через dashboard) — ETH/BTC entries не отбрасываются. Новый ключ в SETTINGS_REGISTRY.
- **Auto-blacklist**: новый параметр `auto_blacklist_days = 12` (was 14) + release patch в `scripts/auto_blacklist.py` — symbols с recent net>0 AND WR≥50% автоматом выпускаются. 3 новых SETTINGS_REGISTRY ключа (release_min_trades/wr/net).
- **Часы 14, 16, 20 UTC** заблокированы (`real_blocked_hours_utc`) — saved ≈$76/7d.
- **ASTERUSDT + WLFIUSDT** в blacklist на 14d (manual).
- **tp_order_type=Limit** — partial TPs теперь maker (0.018% vs 0.055% taker) — экономия ~$25/мес. Hard-coded `"Market"` в `order_executor_v3.set_position_stop_loss` заменён на `config['financial']['tp_order_type']`.
- **fallback_tp_min_r=3.0** — single TP на полный qty когда position слишком малая для split на 3 partial. BTCUSDT 0.001 был без TP → manual fix через Bybit API (orderId 7b2af376) + код patch для future.
- **Risk Officer LLM=Sonnet** (was Haiku) — лучше analytical для CAUTION decisions. Через `risk_officer_llm_model` POST.
- **ML scaler анализ**: модель работает (AUC 0.728, calibrated bucket P=0.6-0.7 → real WR 79.5%). НЕ активировать сейчас — scale-down при текущих всех-positive buckets даёт −34% PnL. Триггер re-evaluate: bucket P≥0.7 накопит 30+ trades. Связано: [[real-trades-baseline]]
- **Insights tab** в /v2.html: `GET /api/insights?source=paper|real&strategy=X&days=N` → 6 metric cards (per-hour, top winners/losers, spike buckets, ML calibration, close reasons, fees). Каждая с ⓘ explainer modal описывающим SQL source + actionable insight.

## 4. Risk Officer / Meta-labeler tooltips (UI)
- 5 toggles в Feature Toggles секции получили ⓘ explainer кнопки → native `<dialog>` modal с полным описанием (что/как/когда включать/риски/что мониторить).
- Множество iteration по UI: popover→overflow clipped → переписал на `<dialog>.showModal()` top-layer rendering.
- Auto-refresh пропускает 30s tick если открыт modal или фокус на input/select — раньше каждые 30s закрывал modal и сбрасывал filters.

## 5. Gerchik feed listener (Telethon) — scaffold готов, ждёт credentials
- `/root/gerchik-trading-agent/src/feed_listener.py` — Telethon user-session bridge, слушает @GTE_Pro channel (-1001264604717), auto-forward на @GTE_AI_TradingBot. Удаляет ручной forward шаг.
- systemd unit `gerchik-feed-listener.service` зарегистрирован но не enabled — ждёт TG_API_ID/HASH/PHONE.
- Артём пытался создать app на my.telegram.org но получил ERROR — отложили.

## Why session важна
Артём явно попросил «делай больше и правильнее чем ожидал» + жёсткие правила работы. После hook activation всё пошло строго по плану — TaskCreate первым действием, прогресс-бар видимый, без болтовни. Также первый раз глубоко влез в Insights/ML — теперь у Артёма есть постоянный self-service tool вместо «дёргать Claude каждый раз».

## How to apply
- Insights tab — пользоваться regularly когда хочешь посмотреть статистику по фильтрам без новых SQL запросов.
- Trading config snapshot закоммичен в `255b290` (`config: snapshot live state — today's POSTs + accumulated MFE-calibration`). Перед сменой mode/strategy parameters проверять что прежний снимок закоммичен.
- Все 5 toggles в Risk Officer + Meta-labeler сейчас в безопасном состоянии (либо OFF, либо shadow). Не активировать без пересмотра по [[real-trades-baseline]] критерию (300-500 real trades).
- Telethon listener — ждёт API_ID/HASH; когда получит — `python3 -m src.feed_listener --auth` для первичной auth.

## Связанные memory
[[strict-plan-rules]], [[real-trades-baseline]], [[no-tables-tg-forward]], [[oauth-force-refresh]], [[bybit-signing-order]], [[real-trades-truth]], [[query-write-swallow]], [[hybrid-mode]]
