---
name: systemctl timestamps for JS consumption
description: ActiveEnterTimestamp format trap — always pass --timestamp=unix and convert to ISO-8601 UTC before returning to browser
type: feedback
originSessionId: 7da703ef-c9f9-47d8-9238-52d53b1a1d23
---
`systemctl show --property=ActiveEnterTimestamp` returns strings like `Tue 2026-04-21 12:38:12 MDT`. Browsers cannot reliably parse the TZ abbreviation — `new Date("...MDT")` returns Invalid Date (NaN time), but the Date object itself is truthy, so `if (d)` checks silently pass and downstream `_timeAgo(d)` prints garbage or empty.

**Why:** Dashboard's "up Xh Xm" indicator + GA "Last restart" label both relied on `new Date(apiString)`. When the API returned systemd's default format, the uptime display went blank without any error. Diagnosed 2026-04-21 after signalbot cooldown_bars restart.

**How to apply:**
- Any endpoint that returns systemd timestamps MUST call `systemctl show --timestamp=unix`, parse `@<epoch>`, and return `datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()`.
- Never return raw systemd human-readable timestamps to the browser.
- Same pattern if adding other endpoints that surface `InactiveEnterTimestamp`, `StateChangeTimestamp`, etc.
- On the frontend side, even if you trust the API, treat Date parse failures explicitly: `if (isNaN(d.getTime())) return '';` — `if (d)` is NOT a valid guard.
