---
name: tutor-live-tools
description: "wife-english-tutor has Anthropic tool-use for live BTC/ETH price (Bybit) and weather (wttr.in); don't let bot answer market/weather from LLM memory"
metadata: 
  node_type: memory
  type: project
  originSessionId: 684f23a1-5fd6-499b-a3a9-251bef4fdb6b
---

В `wife-english-tutor` подключены live-tools в Claude через Anthropic tool-use:
- `get_crypto_price(symbol)` → Bybit `/v5/market/tickers?category=spot` (no key)
- `get_weather(city)` → wttr.in `?format=j1` (no key)

Tools определены в `bot/tools.py`, loop — в `bot/claude_client.py:call_claude(..., tools=, tool_runner=)`. Реестр `TOOL_SPECS + run_tool` подключён в `bot/llm.py:reply_for_turn`. System prompt явно запрещает угадывать цены/погоду из памяти.

**Why:** Артём 2026-05-14 поймал бот на BTC=$79k когда реальная цена ~$81k — Claude цитировал тренировочные данные. Сейчас на любой market/weather-вопрос бот гарантированно делает tool-call.

**How to apply:**
- Расширять список: добавь tool в `TOOL_SPECS` + dispatch в `_DISPATCH` в `bot/tools.py`. Никакого дополнительного wiring не нужно — `call_claude` уже передаёт всё.
- Если бот опять начнёт «галлюцинировать» числа — проверь `grep "tool " /root/wife-english-tutor/logs/tutor.log`: если tool_use не вызывается, причина либо в system prompt (LIVE DATA TOOLS блок снесли), либо в передаче tools (потерян `tools=TOOL_SPECS, tool_runner=run_tool` в reply_for_turn), либо модель не поддерживает tools (Haiku 4.5+ поддерживает).
- Если tool падает (`error: ...` в логе), это пойдёт в Claude как tool_result — он скажет «I can't check right now» естественным языком, не упадёт.
- Stream-вариант (`call_claude_stream`) tools НЕ поддерживает — text-only. `reply_for_turn_stream` пока не учит tools; если /api/voice захочет live data в стриме, придётся добавить отдельный non-stream первый round или mid-stream tool injection.
