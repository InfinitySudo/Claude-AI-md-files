---
name: project_estimator_agent_autonomy
description: "Siding estimator AI agent — self-learning (rules) + autonomous measurement (trace) work, 2026-06-02"
metadata: 
  node_type: memory
  type: project
  originSessionId: 67a14daf-af74-4998-8c45-196c15d3320c
---

Made the TSA siding estimator agent actually learn + measure itself (2026-06-02). It used to demand "give me all the data" because it couldn't measure and never persisted/recalled corrections. Audit found: learned_rules table empty, system prompt self-contradicted ("always read rules" vs "don't waste time reading rules"), calculate_siding_bom used hardcoded defaults, two disconnected stores (ai_trace_examples vs learned_rules).

**Repo:** `/root/siding-estimator-bot/` is now its OWN git repo → GitHub `InfinitySudo/siding-estimator-bot` (private, branch **master**). `.env` (has `TSA_INTERNAL_SECRET`, bot token) is gitignored — never commit it.

**Wave 1 — learns from corrections** (siding_tools.py + siding_estimator_bot.py):
- `live_knowledge_block()` injects active `learned_rules` + `estimator_memory/rules/*.md` into the system prompt EVERY run → knowledge is always present, not the model's choice to fetch. Saved correction shows up next turn = the learning loop.
- Prompt: removed the contradiction; Rule #0b = any number/ratio/material correction → immediate `save_learned_rule` (no "учту" without a tool call); #0c = draft-first, don't beg for data.
- `calculate_siding_bom` parses a learned waste% override (regex from rule_text scoped by siding_type) instead of hardcoded default; cites the source.

**Wave 2 — measures itself** (OnTime backend + bot):
- Calibration guard: `_calibration_confidence()` in main.py — AI `px_per_ft` is checked against the median of the OTHER calibrated sheets in the set (sheets share scale) + implied-size plausibility. Low-confidence scale is REFUSED, not applied (areas ∝ 1/scale² — a wrong scale ruins everything; there's a prior $1.7M-sqft incident). `ai_calibrate_sheet` returns confidence/reasons; medium tagged `⚠`.
- `POST /api/estimates/{eid}/auto-trace` (main.py, **internal-secret auth** via header `X-Internal-Secret` == env `TSA_INTERNAL_SECRET`, set in both /root/ontime/backend/.env.bot and /root/siding-estimator-bot/.env): loops elevation sheets, calibrate+trace headlessly, skips low-confidence-calibration sheets → `needs_manual_calibration`. Cap 12 sheets/run. Reuses `ai_calibrate_sheet`/`ai_trace_sheet` called directly (bypassing Depends).
- Bot tool `auto_trace_estimate(estimate_id)` calls it then `get_ontime_estimate`; prompt ⑤: at takeoffs_count=0 measure itself (don't send human to trace), flag `needs_manual_calibration` sheets, cross-check total wall sqft vs similar projects (>25% → flag_for_review).

**Not done (Wave 2.3, optional ML):** polygon/takeoff precision — per-siding-type relevant few-shot from Ihor's hand-traces (ai_trace_examples is currently company-wide). Accuracy of CV/AI trace itself is the remaining autonomy cap. NOT yet tested on a real estimate (Artem will pick one). Related: [[project_ai_trace_teach]], [[feedback_cv_trace_over_ai]], [[project_estimator_ai_memory]], [[project_estimating_industry_rules]], [[feedback_anthropic_key_scoped_estimator]].
