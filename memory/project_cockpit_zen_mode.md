---
name: project-cockpit-zen-mode
description: "cockpit.html (Command Center dashboard) имеет 3 режима скрытия — ZEN (hide bottom panels), col-collapsed (hide left column), full hyper-zen (Z+C). Hotkeys Z, C. Planet orbits эллиптические по всему экрану."
metadata: 
  node_type: memory
  type: project
  originSessionId: 68e543d1-1602-43c1-ba65-8b847b8f853f
---

## Cockpit dashboard (`/var/www/dashboard/cockpit.html`) — режимы видимости

С 2026-05-25 в cockpit добавлены два независимых toggle-режима + улучшена планетная анимация. Все в [[feedback-cockpit-unversioned]] (правки только на диске VPS).

### Режимы
| Кнопка / Hotkey | Что делает |
|---|---|
| `◯ ZEN` / **Z** | Скрывает все нижние панели (.bottom), .resolver. col-left сужается с 220→180px. Marquee становится opacity 0.6. |
| `◀ HIDE` / **C** | Уезжает влево вся `.col-left` (translateX(-105%)). `.stage` растягивается до left:0. |
| Z + C | Полный «звёздный экран»: только чёрная дыра + планеты + marquee. |

State сохраняется в localStorage (`spacelive-zen`, `spacelive-col-collapsed`). Обе тогглы вызывают `window.__rebuildOrbital()` через ~50/400ms — планеты recalibrate под новый размер `.stage`.

### Planet orbit settings (Kepler engine, ~line 2000-2350)
- `.stage` теперь `left: 0; right: 0; top: 0; bottom: 28px` — занимает **весь экран** (раньше bottom: 258px → 25% пустого места снизу).
- `stretchX = min(5.0, max(1.0, (cx-margin)/maxR))` — эллиптический stretch до edge экрана по X.
- `stretchY = min(3.0, max(1.0, (cy-margin)/maxR))` — аналогично Y.
- `safeMin = max(exclusion, maxR * 0.75)` — внутренняя планета на 75% пути от центра к краю (раньше 0.38 — кучковались).
- **Phase 2.5 clamp** — эллиптический (`rNorm = √((dx/limX)² + (dy/limY)²)`), не круговой. Раньше круговой clamp `if d > maxR` вгонял планеты в маленький круг, отменяя stretchX.

### Топ-навигация
- `◐ MATRIX` — theme toggle
- `◯ ZEN` — zen mode
- `◀ HIDE` — col collapse
- `📊 TILES` / `⚙ FULL` / `🎯 LEVELS` — навигация на другие страницы (скрыты в ZEN)

### Связанные правки
- AGENTS-список (#agents-list) — естественная высота, col-left scrollable (overflow-y: scroll) с зелёным scrollbar
- PAPER DELTA timeframe label апдейтится через `setText('paper-period', PERIOD)`

Связано: [[feedback-cockpit-unversioned]], [[project-dashboard-v2]].
