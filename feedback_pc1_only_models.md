---
name: pc1-only-model-tags-trap-fallback-chain
description: "PC1 имеет custom Ollama model tags (например `qwen2.5:32b-ctx4k`) которых нет на PC2 — fallback chain 404s when configured with PC1-only model name"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2f4c4861-fd60-4f57-b7af-c4260e03075c
---

`VT_LOCAL_LLM_TOOL_MODEL=qwen2.5:32b-ctx4k` на PC1 — это **локально созданный modelfile-tag** (`32B base + custom context window 4096`). На PC2 такого tag нет — есть только stock `qwen2.5:32b-instruct-q4_K_M`. Когда fallback chain пытается PC2 — получает **404 model not found**, instant — выпадает на Claude, и весь pipeline ест ~15-17 секунд per turn.

**Why:** 2026-05-15, latency optimization session. Voice-tutor c tools (memory extraction, weather, crypto, web) использует `VT_LOCAL_LLM_TOOL_MODEL`. PC2 install только stock tags, PC1-only tag fail на PC2. Fallback chain работал, но всегда падал в Claude после 404 — local стек никогда не активировался полностью.

**How to apply:**
- При установке нового PC в fallback chain — `curl :11434/api/tags` на PC1 и PC2, **diff**: PC1-only tags будут 404 на PC2.
- Для shared chain — использовать только модели присутствующие на обоих PC:
  - `qwen2.5:7b-instruct-q4_K_M` (plain chat)
  - `qwen2.5:14b-instruct-q4_K_M` (tool calling — fast enough, на обоих)
  - `qwen2.5:32b-instruct-q4_K_M` (stock 32b, тоже на обоих)
- Либо `ollama pull` нужные tags на secondary PC через ssh+powershell.
- Либо разделить config: `VT_LOCAL_LLM_TOOL_MODEL_PC1` / `_PC2` — но это refactor `llm_local.py`.

После fix 2026-05-15: `VT_LOCAL_LLM_TOOL_MODEL=qwen2.5:14b-instruct-q4_K_M` (вместо `32b-ctx4k`). 14b на обоих PC, warm ~0.9s, cold ~15s. Tool calling качество не падает (per code comment в `llm_local.py`: "14b reliably calls tools in ~2.7s hot").

Связано: [[project_pc1_homelab_active]] (PC1 modelfiles), [[project_pc2_homelab_active]], [[project_tutor_latency_pipeline]].
