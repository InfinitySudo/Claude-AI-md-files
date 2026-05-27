---
name: Siding Takeoff Industry Rules
description: numeric ratios + workflow conventions for OnTime Estimating BOM engine — collected 2026-05-04
type: project
originSessionId: caee81af-88d6-4f38-9e35-a9e3b71df54e
---
Researched standard practice (PlanSwift/On-Screen Takeoff/Hardie/CertainTeed/Kalouzie) для построения BOM engine в OnTime Estimating.

**Unit:** 1 square = 100 sqft (универсально).

**Geometry decomposition:**
- Rect (стены прямоугольные): L × H
- Triangle (гэйблы): B × H / 2
- Net wall area = gross − openings

**Default openings когда не вытащили из чертежа:**
- Door: 3' × 7' = 21 sqft, perimeter = 20 LF
- Window: 3' × 4' = 12 sqft, perimeter = 14 LF

**Waste factors (multiply net area):**
- Vinyl lap: 1.05–1.10
- Fiber cement (Hardie) horizontal lap: 1.10 simple / 1.15 complex
- Vertical / board & batten: 1.12–1.15
- Shake / shingle: 1.10–1.15
- Многоугольный дом, gables, обилие openings: до 1.20

**Accessory rules:**
- **Starter strip**: bottom LF каждой обшиваемой стены × 1.05–1.10
- **J-channel**: ΣLF perimeter всех openings (windows + doors); быстро = 2pcs/window + 1.5pcs/door (pieces 12ft)
- **Outside corner post**: 1 per corner, height covered by 12ft pieces
- **Inside corner**: J-channel или специальный inside corner trim
- **Soffit area**: eaves+rakes perimeter (LF) × overhang width (ft); waste +10–15%
- **Fascia LF**: total eaves + rakes; waste +10%
- **Drip edge / Z-flashing**: top of wall LF + over openings horizontal LF

**Hardie specifics:**
- HardiePlank 7.5" exposure: 13–15 planks/square, 12ft plank ≈ 7.5 sqft
- HardieTrim per opening + per corner; fasten 16ga finish nails
- Different exposure (5", 6.25", 8.25") меняет план/sqft

**Workflow conventions (mirror PlanSwift):**
1. Calibrate per sheet — site plan vs floor plan vs elevation = разные scale, scale переносить НЕЛЬЗЯ
2. Tools: Linear (LF), Area (polygon), Count
3. Polygon: click corners, real-time sqft при закрытии
4. Subtract Area: openings вычитать из родительской стены, не считать отдельно
5. Snap to plan nodes — mis-click 5px на 1:100 = несколько футов реальных размеров
6. Один person becomes internal expert; assembly library с naming convention для consistency

**Source pages:**
- kalooziecomfort.com/estimating-siding-squares-and-waste/
- nedesestimating.com/the-ultimate-planswift-how-to-guide
- inchcalculator.com/vinyl-siding-calculator/
- weathershieldroofers.com/hardie-siding-calculator/

**How to apply:** Эти ratio'я кодируются в `_bom_for_takeoffs()` (Step 5). Не зашивать "magic numbers" в frontend — все формулы на бэке, frontend только показывает результат. Waste factor должен быть editable per-estimate (default Hardie 1.12, overrideable).

**Catalog mapping (важно для BOM Step 5):**
- В `materials` table уже 1712 purchase items + 233 labor rates (Roofmart Calgary North/South vendor_id 8/9; Convoy/Gentek/Kaycan тоже там)
- Categories: `Cladding / Fiber Cement siding / James Hardie Products`, `Cladding / Metal Cladding / LUX`, `Cladding / Vinyl / Royal`, `Cladding / Sagiper`, `Cladding / Chamclad`, `trims`, `flashing`
- Labor rates с unit `sft`/`lft` (Hardie Plank $1.82/sft, Hardie Panel+EZ $3.08/sft, Hardie Trim $1.40/lft, EZ.X corners/trims) — соответствуют industry ratios
- BOM engine НЕ должен генерить SKU — мэппить takeoff kind → catalog material (по category prefix или по name match)
- Альберта building code 9.36: permeable WRB обязателен под cladding (Tyvek/blue skin); rainscreen Calgary — рекомендован Calgary climate ready measures, но не mandatory; добавить в BOM template как стандарт
- Standard openings когда чертёж не вытащит размеры: door 3'×7'=21sft, window 3'×4'=12sft (default только для placeholder; реальные значения от takeoff polygon'а)
