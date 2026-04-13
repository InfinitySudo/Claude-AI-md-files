---
name: Chart.js freezes browser without bounded parent height
description: Wrap every Chart.js canvas in a fixed-height div, otherwise the responsive resize loop grows the canvas forever
type: feedback
originSessionId: 02a721df-beff-4bfd-bf57-391bd21672c8
---
Every Chart.js canvas in `TRADING_DASHBOARD.html` must sit inside a parent div with an explicit `height` (or `max-height`) when used with `responsive: true, maintainAspectRatio: false`. Otherwise the resize observer loops forever and freezes the browser tab — Artem's browser died on the "TP Hit Funnel" chart until I wrapped the canvas in `<div style="position: relative; height: 280px;">`.

**Why:** Chart.js with `maintainAspectRatio: false` sizes the canvas to fill its parent. When the parent has no height constraint, it takes the canvas's current height as content height, which feeds back into the next resize cycle, growing unboundedly. The dashboard's other charts (`pnl-chart`, `trades-chart`) live inside `.charts-grid` which indirectly bounds them via grid row sharing, so they settle; a chart alone in a full-width `.chart-container` does not.

**How to apply:**
- Any new `<canvas>` going into the dashboard: wrap it in `<div style="position: relative; height: <N>px;">` with a concrete pixel height (or vh, but not %). The `.chart-container` class gives you padding/border but NOT a bounded height.
- Don't "fix" a frozen tab by lowering polling frequency or adding animation disables — the root cause is the unbounded parent. Fix the layout.
- Rule of thumb: if you put a Chart.js canvas outside of a grid and don't set a height, you are about to freeze the browser.
