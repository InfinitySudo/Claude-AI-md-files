---
name: project-wrestling-pill-nav
description: "Wrestling bottom-nav — pill-индикатор (framer-motion layoutId), горизонтальный скролл, safe-area-inset, авто-скролл активного таба"
metadata: 
  node_type: memory
  type: project
  originSessionId: c9d2b899-f272-4e25-b502-fa1e0f5284ca
---

С 2026-05-19 (commit b3a576e) `src/components/Layout.jsx` использует pill-style bottom-nav:

- **Pill индикатор:** `<motion.div layoutId="bottomnav-pill">` плавно перетекает между активными табами spring (stiffness 380, damping 32).
- **Icon scale:** активная иконка анимируется до 1.15× + y:-1, spring.
- **Label fade:** подпись появляется только под активным табом (`opacity/height` animate).
- **Haptic:** `navigator.vibrate(10)` на каждый tap.
- **Скролл:** rail с `overflow-x-auto` + `scroll-snap-type: x proximity`, `.bottomnav-rail::-webkit-scrollbar` скрыт в `src/index.css`. Иконки `shrink-0 min-w-[58px]`.
- **Safe-area:** `paddingBottom: max(env(safe-area-inset-bottom), 6px)` — иначе на iPhone Home-indicator резал последний таб.
- **Auto-scroll active:** `useEffect` на `location.pathname` → `scrollIntoView({inline:'center', behavior:'smooth'})` на элементе с `data-nav-active="true"`.

**Why:** Артём хотел "живые кнопки" + горизонтальный скролл как задел на больше табов. Полноэкранный режим iPhone PWA скрывал последнюю кнопку — safe-area фикс снимает это.

**How to apply:** Добавляешь новый таб? Просто пуш в `athleteNav/coachNav/guestNav` массив + ключ в `nav.<key>` всех 9 i18n файлов. Pill/скролл подстроятся автоматически.

Связано: [[project_wrestling_i18n_9langs]], [[project_wrestling_v2]].
