---
name: feedback-toast-pointer-events
description: Toast/snackbar с opacity:0 без pointer-events:none молча съедает клики по элементам под ним
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b9744314-006e-4417-b028-5600b451016c
---

Любой `position:fixed` overlay (toast, hidden modal, splash) с `opacity:0` но БЕЗ `pointer-events:none` остаётся click-target'ом. Пользователь видит пустое место, кликает, ничего не происходит.

**Why:** В дашборде v2 (2026-05-13) Артём пожаловался что Settings tab перестаёт нажиматься после Save. Причина: `.toast` сидит `top:16px right:16px z-index:1000`, через 3.5s становится opacity:0 — но геометрически остаётся над Settings/Symbols/GA tabs и съедает таппы.

**How to apply:**
- Всегда добавлять `pointer-events:none` для toast/snackbar (и любых hidden overlays). Переключать на `auto` только если элемент должен быть кликабельный.
- Опция-2: убирать элемент из DOM (display:none) после анимации — но дороже для re-fade-in.
- Похожий класс ошибок: `visibility:hidden` отключает clicks, `opacity:0` — нет. CSS gotcha.

Связано с [[feedback-chartjs-unbounded-height]] (UI-уровневые ловушки в dashboard'е).
