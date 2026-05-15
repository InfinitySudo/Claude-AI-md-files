---
name: ollama-race-shadow-emails-triage
description: "PK1+PK2 LLM race helper в emails-bot, shadow-режим против Claude Haiku triage с 2026-05-13"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7b14e18d-63a6-4d91-a38e-33d997ae386b
---

**Цель:** проверить можно ли заменить Claude Haiku 4.5 на локальный qwen2.5 (PK1+PK2 race) в emails-optimization triage без потери качества. Экономия — API-токены Haiku на каждое письмо.

**Race helper:** `app/ollama_race.py` (в `/root/emails-optimization`)
- `ollama_race(model, messages, system, tools, max_tokens, timeout)` — параллельный POST на PK1+PK2 Ollama, first-success wins.
- `claude_tools_to_ollama(claude_tools)` — конвертит Anthropic `input_schema` → OpenAI `function.parameters`.
- `extract_tool_call(resp, tool_name)` — достаёт arguments из Ollama `tool_calls`.
- Nodes из env `OLLAMA_NODES`, по дефолту `http://100.99.211.123:11434,http://100.73.22.1:11434`.

**Shadow интеграция в `app/triage.py`:**
- `_shadow_one(row)` — запускается после `_persist`, идемпотентно сохраняет JSON в `emails.triage_shadow_json`.
- Toggle через env `EMAILS_TRIAGE_SHADOW=1` (в `emails-poller.service` Environment=).
- Модель: env `EMAILS_TRIAGE_SHADOW_MODEL` (дефолт `qwen2.5:14b-instruct-q4_K_M`).
- Timeout: env `EMAILS_TRIAGE_SHADOW_TIMEOUT` (дефолт 120s — длинный system prompt + холодный VRAM load).

**Новые колонки в `emails`:** `triage_shadow_json`, `triage_shadow_winner`, `triage_shadow_latency_ms`, `triage_shadow_model` (см. `app/db.py:init`).

**Как смотреть статистику:**
```
cd /root/emails-optimization && python3 -m app.triage --shadow-stats
```
Сравнивает по: `triage_class`, `business_id` (из labels `biz:*`), `project_id`, `urgent_subcategory`. Latency + race winner counts.

**Promote critterion:** ≥90% совпадение по `triage_class` И `business_id` на 50+ shadow rows → можно отключить Claude (поменять `_triage_one` чтобы дёргал `ollama_race` вместо `safe_create`, держать Claude как fallback). Если <90% — оставить Haiku.

**Известные расхождения (на момент 2026-05-13, n=4):**
- triage_class: 50% — Ollama 14b чаще говорит "delegate" вместо "mute" для автоматических notifications (Airbnb/EOS/etc). На 32b может быть лучше.
- business_id: 100%, urgent_subcategory: 100% (потому что все non-urgent).

**Warm latency:** ~1.8-2.2s на длинный triage prompt c tools (qwen2.5:14b на RTX 3090).
**Cold latency:** ~16s на первый request (VRAM load).

Якоря: [[project_pc1_homelab_active]], [[project_pc2_homelab_active]]
