---
name: feedback-ontime-inline-edit-blur-trap
description: "OnTime inline-поля — onChange пишет в task, а onBlur сравнивает e.target.value!==task.field → всегда equal → patch не вызывается, правки не сохраняются"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 520ebb72-e212-4d77-8428-d58bac900b5b
---

Антипаттерн в OnTime React-компонентах (нашёл в `ServicePage.jsx` TaskDetailModal, title + description, 2026-05-29): inline-поле сделано как `value={task.x}` + `onChange={setTask({...task, x})}` + `onBlur={e => e.target.value !== task.x && patch({x})}`. Баг: onChange уже обновил `task.x` на каждое нажатие, поэтому в onBlur `e.target.value === task.x` ВСЕГДА → `patch` не вызывается → **дописанный текст не сохраняется** (жалоба Артёма про description сервис-задачи).

**Why:** сравнение идёт с живым state, который мутируется при печати, а не с последним СОХРАНённым (серверным) значением.

**How to apply:** держать снимок серверного значения отдельно — `savedRef = useRef({...})`, обновлять его только в `load()` и в `patch()` после успеха (`snapshotSaved(t)`), а в onBlur сравнивать `e.target.value !== savedRef.current.x`. Backend (`ServiceTaskPatch` + `model_dump(exclude_unset=True)` + generic UPDATE в backend/main.py) поле принимает — баг чисто фронтовый. Проверять этот же паттерн в других inline-редактируемых полях (ProjectDetailPage и т.п.). Родственно [[i18n-fallback-trap]] по духу «сравнение/фоллбэк со значением, которое уже не то».
