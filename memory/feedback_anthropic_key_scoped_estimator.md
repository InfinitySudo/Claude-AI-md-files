---
name: anthropic-key-scoped-estimator
description: ANTHROPIC_API_KEY запрещён в OnTime — только TSA_ESTIMATOR_ANTHROPIC_KEY и только в ai_trace.py
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a7860ae7-e5ec-4b08-a0dc-c01b073078ff
---

В `/root/ontime/backend/.env.bot` платный Anthropic ключ хранится как `TSA_ESTIMATOR_ANTHROPIC_KEY` (НЕ `ANTHROPIC_API_KEY`). Читается только в `/root/ontime/backend/ai_trace.py:_make_client()` для AI Trace в эстиматоре. Любой другой модуль OnTime, которому нужен Claude API, должен сначала спросить Артёма (не подцеплять автоматом).

**Why:** Артём явно сказал 2026-05-25 «используй этот ключ только для TSA Estimator в OnTime app». Глобальное имя `ANTHROPIC_API_KEY` ловится любым случайным `anthropic.Anthropic()` вызовом и утекает за scope — отсюда переименовали в специфичный namespace.

**How to apply:**
- Новые AI-фичи в OnTime — НЕ читать `TSA_ESTIMATOR_ANTHROPIC_KEY` без согласования. Завести свою переменную (`TSA_FOO_ANTHROPIC_KEY`) или использовать OAuth-fallback из ai_trace.
- При аудите `os.getenv("ANTHROPIC_API_KEY")` в OnTime — это анти-паттерн, исправлять.
- Связано: [[project_tsa_estimating]], [[feedback_ai_trace_enabled]].
