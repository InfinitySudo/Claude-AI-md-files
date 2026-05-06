---
name: OnTime notification i18n
description: Per-recipient lang for notifications — где живёт инфра и какие call sites уже переведены
type: project
originSessionId: 5d50c081-8779-4229-bd8c-a5ee134586c9
---
С 2026-05-06 notifications рендерятся на языке получателя (`users.lang` ∈ en/ru/uk).

**Инфра:**
- `users.lang` колонка (NULL = legacy → fallback 'ru' в `_user_lang`)
- `backend/notif_i18n.py` — `NOTIF` dict (title/body per key per lang) + `DIGEST_LABELS` + `nt(key, lang, kind, **vars)` + `dl(key, lang)`
- `notify_with_store(..., key=, vars=)` и `notify_role_with_store(..., key=, vars=)` рендерят per-user
- `_notify_foremen_on_project(..., key=, vars=)` и `_notify_ew_watchers(..., key=, vars=)` — обновлены
- Frontend: `setLang()` и `syncLangToBackend()` PATCH `/api/me/preferences {lang}`; вызывается на boot из `App.jsx`

**Уже переведены:**
- Extra Work: `proposed`, `vp_approved`, `pm_approved`
- Director digest (`run_director_digest` + `_format_director_digest(stats, stuck, today, lang)`)

**Why:** Артём 2026-05-06: "vibran english yazik no soobsheniya prihodyt na polovinu russkie".

**How to apply:**
- При добавлении новых notification call sites — добавь key в `notif_i18n.NOTIF`, передай `key=` и `vars=` в `notify_with_store`/`notify_role_with_store`/`_notify_foremen_on_project`/`_notify_ew_watchers`. Не пиши hardcoded RU/EN.
- Ещё НЕ переведены: EW `materials_ordered`/`done`/`invoiced`/`paid`/`rejected`, transfer notifications (`/api/workers/.../transfer-request`), daily nudge, deliveries TG-briefing, OT alerts. Для каждого — добавить key в NOTIF и swap call site.
- TG broadcast (`tg_broadcast_event`) идёт в company-wide chat — это не per-user, оставляем EN-only.
