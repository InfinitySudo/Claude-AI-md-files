---
name: GA Symbols — Single Source is Symbols Editor
description: GA optimizer reads symbol list live from config/symbols.json (Symbols Editor); no separate GA-symbols store
type: feedback
originSessionId: 7da703ef-c9f9-47d8-9238-52d53b1a1d23
---
GA optimizer symbol list comes from **config/symbols.json** (the Symbols Editor) — NOT from a separate `ga_symbols.json`.

**Why:** Артём редактирует список монет в Symbols Editor и ожидает что GA автоматически подхватит изменения. Отдельный ga_symbols.json быстро рассинхронивается (было: editor=195, ga_symbols=113) и вводит в заблуждение.

**How to apply:**
- `/api/ga/symbols` GET derives live from SYMBOLS_PATH via `_ga_active_symbols()` helper (tier_1 + tier_2 + tier_3, deduped)
- POST `/api/ga/symbols` is removed — list is read-only in GA panel
- `/api/ga/run` uses `_ga_active_symbols()` as default if payload has no `symbols`
- GA Symbols panel in dashboard is read-only textarea (labeled "synced from Symbols Editor")
- `data/ga_symbols.json` archived 2026-04-21 as `.deprecated_*`
- If adding new symbol-source flows, always route through `_ga_active_symbols()` — don't introduce a parallel store
