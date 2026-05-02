---
name: OnTime BOM replace trap (project_materials wipe)
description: Saving a project with shorter material list silently wipes ALL prior BOM rows on that project — DELETE-then-INSERT pattern in _set_project_materials
type: feedback
originSessionId: 326669b3-b9b2-4025-a64a-317eeb368734
---
В `main.py` функция `_set_project_materials` (около line 2168) при сохранении проекта делает `DELETE FROM project_materials WHERE project_id = ?` и потом INSERT'ит то, что прислали. Никакого diff/upsert.

**Why:** 2026-04-25 Артём загрузил новый Stack labor каталог (91 → 141 materials), и при каком-то save проекта (видимо через Stack BOM upload UI) BOM на 16 active проектах слетел в ноль. Восстанавливал из бэкапа.

**How to apply:**
- Перед любым PATCH/POST /api/projects с `materials` в body — проверять, что список материалов НЕ короче текущего, иначе предупреждать.
- Если делается Stack import / BOM upload — НЕ передавать пустой/неполный materials list "в довесок", иначе зачистит существующее.
- Долгосрочно: переписать `_set_project_materials` на diff (compute add/update/remove sets, only DELETE explicit removals) + warn-confirm в UI если удаляем >0 строк. Не делал пока — понадобится, если повторится.
- Перед массовыми операциями — backup БД (см. tsa.db.before-bom-restore-* как пример).
