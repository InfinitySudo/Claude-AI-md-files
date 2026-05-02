---
name: OnTime Labor vs Purchase Materials
description: Two distinct kinds of "materials" in OnTime — labor install rates vs vendor purchase prices. Never mix them.
type: feedback
originSessionId: 326669b3-b9b2-4025-a64a-317eeb368734
---
В OnTime **два разных вида материалов с двумя разными ценами**:

1. **Labor materials** (install rates) — то, что рабочие УСТАНАВЛИВАЮТ. Цена = ставка за установку (per unit). Используется для расчёта бюджета проекта (сколько заплатим бригаде).
2. **Purchase materials** (vendor offers) — то, что ПОКУПАЕМ у поставщиков (Roofmart и т.д.). Цена = закупочная стоимость. Используется для procurement/orders/POs.

**Why:** Это разные сущности, разная экономика, разные таблицы прайсов. Перепутаешь — поплывут расчёты бюджета объекта И закупки/заказы материалов одновременно. Артём явно подчеркнул: "ochen vajno ponyat i nichego ne pereputat".

**How to apply:**
- НИКОГДА не делать fallback с `materials.price` (labor) в колонки vendor catalog — это две разные шкалы.
- Перед любой правкой каталожных endpoint'ов / SQL: уточнить у Артёма, для какого вида материалов это.
- Если видишь, что Catalog endpoint возвращает прочерки — НЕ маскировать labor-ценами; сначала разобраться, куда делись vendor offers (vendor_materials).
- Раньше `materials` хранил purchase-items (Trim, Shake, VeneerBrick — без "Labor" в названии), а `vendor_materials` хранил офферы от вендоров. После 2026-04-25 05:37 в `materials` лежат labor items ("... - Labor"). Возможно, нужно разделение через флаг (kind='labor'|'purchase') или две таблицы — уточнить у Артёма.
