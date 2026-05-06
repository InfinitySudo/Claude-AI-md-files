---
name: Estimating без Claude API
description: regex + ручной edit вместо Vision API для extraction; решено 2026-05-04 после теста на 3 архитекторских PDF
type: feedback
originSessionId: caee81af-88d6-4f38-9e35-a9e3b71df54e
---
В модуле OnTime Estimating НЕ использовать Claude/OpenAI Vision API для парсинга title-block. Только regex (см. `_extract_blueprint_metadata` в main.py) + кнопка-карандаш ✏️ на детальной странице для ручной правки.

**Why:** На 3 реальных архитекторских PDF от Артёма (Block 6 / SHCD / Bldg02) regex дал address в 1/3 случаев чисто (estimate #3), в 1/3 поймал адрес консультанта вместо проекта (estimate #5 — Arcadis title block содержит 5+ адресов разных дисциплин), в 1/3 не нашёл (estimate #4 — subset страниц без title block). Vision API дал бы 95%+ за ~$0.005/PDF, но Артём предпочёл вариант B = бесплатно + 60s ручной правки на estimate, чем A = API key + автоматизация. 8-10 estimate'ов/нед × 60s = 8-10 минут/нед на правки — приемлемо.

**How to apply:** Не предлагать Vision API для extraction title-block в estimating, разве что Артём сам поменяет решение. Если regex захочется улучшать — делать это в `_extract_blueprint_metadata`, не вынося наружу. На phase 2/3 (tracing canvas, vector auto-extract геометрии) этот запрет НЕ распространяется — там Vision может пригодиться для классификации sheet'ов (elevation/floor plan).
