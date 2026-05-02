---
name: Bybit signing order trap
description: bybit_api.py _request("GET") signs sorted params but used to send unsorted — silent 401 on auth-required endpoints with non-alphabetical insertion order
type: feedback
originSessionId: 5eb329a9-fa6d-4ab4-9f21-be7e401708fa
---
`bybit_api.py:_request("GET")` signs params in alphabetical-sorted order, but `requests.session.get(url, params=dict, ...)` serializes in dict insertion order. If insertion order != alphabetical, signature ≠ what's sent → Bybit returns 401 with `Error sign, please check your signature generation algorithm`.

**Why:** Bug ate every TP/SL execution-history query and any auth endpoint where caller passed `{category, symbol, limit}` (insertion: c,s,l; alphabetical: c,l,s). Public endpoints like `/v5/market/kline` silently worked because they don't validate signature.

**How to apply:** Fixed 2026-04-29 — _request now builds the URL manually with sorted querystring (`f"{url}?{query_string}"`) and passes it as a string, no `params=` kwarg. ANY future helper that signs Bybit private endpoints must sign exactly the bytes that hit the wire. Easy to break if someone reverts the change.

**Detection:** `retMsg=Error sign...` in dashboard log = this bug. Test with `/v5/execution/list?category=linear&symbol=X&limit=50` — exposes it because both sort orders differ.
