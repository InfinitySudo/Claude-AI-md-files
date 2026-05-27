---
name: Bybit empty result truthy-trap
description: Bybit V5 endpoints (особенно /position/trading-stop) на success возвращают retCode=0 с result={}; `if not res` интерпретирует это как failure
type: feedback
originSessionId: 7ecab4cc-5fb7-4e8a-9ff9-8754cff466ae
---
Rule: При работе с Bybit V5 wrapper-функциями, которые возвращают result-dict, **проверяй failure через `is None`, а не через truthy-check**. Bybit регулярно отдаёт `retCode=0` с `result={}` на полный success — это нормальный contract API.

**Why:** 2026-05-10 gerchik-agent потерял $1.20 на XRPUSDT за 2 секунды. `set_trading_stop` (real_executor.py:140) проверял `if not ts_res:` — и т.к. Bybit отдал `result={}`, `bool({})==False` → caller паниковал и market-close'ил позицию reduceOnly после уже успешного TP/SL attach. Closed PnL: −$0.66 (slippage) + $0.27×2 fees = −$1.20. В журнале НЕ было WARNING'а от _signed_post, потому что retCode реально был 0 — путаница только на стороне caller.

**How to apply:**
- Wrapper-функция должна возвращать `None` ТОЛЬКО при настоящем failure (network exception, retCode!=0, HTTP non-2xx). На success — всегда truthy-dict.
- Если Bybit отдал пустой `result`, заверни через `setdefault('_ok', True)` или верни `{'ok': True}` — explicit truthy.
- Caller: `if res is None` вместо `if not res`.
- Endpoints с empty success-result (известные): `/v5/position/trading-stop`, `/v5/position/set-leverage`, `/v5/position/set-tpsl-mode`, `/v5/account/set-margin-mode`. Все они отвечают `{retCode:0, result:{}}` при успехе.
- Перед merge'ем нового Bybit wrapper'а: один раз вызвать живой endpoint и распечатать `j` чтобы увидеть формат result.

**Связанные файлы (gerchik-trading-agent):**
- `src/bybit_client.py:393` set_trading_stop — добавлен `_ok:True` flag
- `src/real_executor.py:140` — изменён check на `is None`
