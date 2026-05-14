---
name: graph-system
description: "5 knowledge graphs (memory, trading, tutor, ontime, projects) + auto-generated PROJECTS.md digest; new sessions read PROJECTS.md first via MEMORY.md to load full project context"
metadata: 
  node_type: memory
  type: project
  originSessionId: 684f23a1-5fd6-499b-a3a9-251bef4fdb6b
---

`/root/graph-system` (private repo `InfinitySudo/graph-system`). Built 2026-05-14 in a single session.

**Five graphs, all served via `teacher1.constantwrestling.cloud` nginx aliases:**
- `/memory-graph/` — 237 memory nodes from `*.md` frontmatter + `[[wiki-links]]`
- `/trading-graph/` — symbols × strategies × close_reasons from Postgres (uses `realized_pnl_usd − fees_paid_usd`, NOT `gross_pnl_usd` which is final-chunk only; see [[project_realized_pnl_column]] + [[project_fees_accounting]])
- `/tutor-graph/` — wife + son tutors: learners × mistake categories × words × books
- `/ontime-graph/` — workers × projects × materials × vendors (schema-drift tolerant)
- `/projects-graph/` — **master** — 16 GitHub repos × services × hosts × memory

Tech stack: NetworkX in batch + Cytoscape.js front (built-in `cose` layout — fcose UMD on unpkg is broken, see commit `edbaf49`). Generic template at `tools/_template/graph_generic.html` to avoid the trading-template trap where missing `data.stats.total_pnl` killed tutor/ontime rendering silently.

**PROJECTS.md auto-digest** — `tools/projects_graph/build_graph.py` regenerates it every 30 min (systemd timer `graph-rebuild.timer` runs `rebuild-all.sh`). Sections: Recent activity (10 commits), Shared resources (creds-only, symlinked .env skipped), Recent memory edits, Scheduled jobs, per-project block with status icon (🟢/🟡/🔴/⚫), host health-checks, README excerpts, linked memories.

`PROJECTS.md` lives both in `~/.claude/projects/-root/memory/` (auto-loaded into every new session) AND mirrored to `Claude-AI-md-files/` repo. MEMORY.md line 1 points to it with "🗂 Projects digest — START HERE".

**How to use:**
- Open https://teacher1.constantwrestling.cloud/projects-graph/ for the visual; click any project node → see what services it runs, what hosts it serves, which memories cover it.
- Manual rebuild: `/root/graph-system/rebuild-all.sh` (also fires every 30 min via systemd).
- New module template: copy `tools/_template/graph_generic.html`, render it with title/colors/data URL, drop alongside a `build_<name>.py` that emits `{nodes, edges, stats}`. Wire into `rebuild-all.sh` and nginx (see commit `e5acb92` for the pattern).

**Adding new shared secrets** to the detection regex: edit `_CRED_RE` in `tools/projects_graph/build_graph.py` (current: `TOKEN|API_KEY|API_SECRET|SECRET|PASSWORD|PWD|CREDENTIAL|BEARER|OAUTH|PRIVATE_KEY|WEBHOOK`).

**Known gaps (TODO):**
- nginx `Hosts:` column is "—" for many projects because `find_nginx_hosts` greps for the local path; better to map vhosts by `proxy_pass http://127.0.0.1:PORT` and remember the port→project map.
- Memory linkage uses regex aliases — false matches (Sophie hits both voice-tutor and son-french-tutor); switch to explicit `[[wiki-link]]` parsing once enough memories adopt the convention.
- Trading graph aggregates by tuple but doesn't bucket by time window — high-noise from old combos with 1 trade. Add `min_trades` filter to the JSON for cleaner view.
