---
name: Sage Hill 600 Blueskin → SOPRASEAL split (one-time fix)
description: Audit trail of the 2026-05-05 redistribution that moved 78% of legacy "Blue Skin" reports into SOPRASEAL labor on Sage Hill Bldg 600
type: project
originSessionId: 656b7c75-d454-4ed9-a10e-fd40c758b37e
---
Project Sage Hill Commercial Development Bldg 600 (`projects.id=46`) had ~80 daily_report_items pointing at legacy material `Blue Skin` (`materials.id=80`, price 1.4/sft). Plan splits air-barrier labor into:
- `BLUESKIN VP160 + primer - labor` (id 567) — planned 2199.29 sf (22%)
- `SOPRASEAL STICK 1100 TC + Primer SF - Labor` (id 574) — planned 7855.77 sf (78%)

Two failure modes were found 2026-05-05:
1. **Bridade duplication.** When 2-5 workers were on site, each logged the same daily quantity → totals ×N (worst day: 3 workers × 1008 sf). Sum of all entries = 13525.5 sf; max-per-day de-dup = 5860.5 sf.
2. **Wrong material picker.** All entries went to legacy `Blue Skin` (id 80); SOPRASEAL stayed at 0/7855. Real on-site mix almost certainly was mostly SOPRASEAL.

**Fix applied (DB only, no migration script):**
```sql
INSERT INTO daily_report_items (report_id, material_id, quantity, unit_price_snapshot)
SELECT dri.report_id, 574, ROUND(dri.quantity * 0.78, 2), dri.unit_price_snapshot
FROM daily_report_items dri JOIN daily_reports dr ON dr.id = dri.report_id
WHERE dr.project_id = 46 AND dri.material_id = 80 AND dri.quantity > 0;

UPDATE daily_report_items SET material_id = 567, quantity = ROUND(quantity * 0.22, 2)
WHERE id IN (... project=46, material=80, qty>0 ...);

UPDATE daily_report_items SET material_id = 567
WHERE id IN (... project=46, material=80, qty=0 ...);
```

Result: BLUESKIN 2975.6 sf (×1.35 plan), SOPRASEAL 10549.9 sf (×1.34 plan). Both still over-plan because the duplicate-bug wasn't undone — only the redistribution was applied (Артём не выбрал dedup опцию).

Backup: `/root/ontime/backend/tsa.db.bak-before-blueskin-split-20260505-162720`.

**Why:** Артём заметил «13525 sf vs план 2199 sf» и спросил «кто завысил». Это не один rogue report — bridade habit + wrong material. He picked options 2 (redistribution) + 3 (UI guard).

**How to apply:** Если позже подтвердится, что реальный installed ≠ 78/22, можно повторно распределить из бэкапа: `cp tsa.db.bak-before-blueskin-split-20260505-162720 tsa.db && systemctl restart ontime-api`. UI-guard (remaining + over-plan warning) добавлен в `ReportPage.jsx` и предотвращает повторение для других проектов.
