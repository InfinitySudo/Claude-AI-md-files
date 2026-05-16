#!/usr/bin/env python3
"""Parse memory/*.md into a knowledge graph JSON.

Output: /root/.claude/projects/-root/memory/graph.json
Schema:
  { nodes: [{id, name, title, type, summary, size}],
    edges: [{source, target}] }

A "node" is a memory file. type is read from frontmatter `metadata.type`
(user / feedback / project / reference); files without frontmatter become
type=other.

An "edge" is a `[[name]]` wiki-link from one body to another file's name.
Dangling links (target name with no file) are kept as type=stub nodes —
visible as the "TODO" entries the memory contract allows.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
MEMORY_DIR = ROOT
OUT = MEMORY_DIR / "graph.json"
MD_OUT = MEMORY_DIR / "MEMORY_DIGEST.md"

# Skip non-memory files like the index and this script.
SKIP = {"MEMORY.md", "MEMORY_DIGEST.md", "PROJECTS.md",
        "TRADING_DIGEST.md", "ONTIME_DIGEST.md", "TUTOR_DIGEST.md",
        "build_graph.py", "graph.html", "graph.json"}

_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_LINK_RE = re.compile(r"\[\[([a-z0-9][a-z0-9_-]*)\]\]")
_NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
_TYPE_RE = re.compile(r"type:\s*(\w+)")
_DESC_RE = re.compile(r"^description:\s*(.+)$", re.MULTILINE)


def parse_file(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    front_m = _FRONT_RE.match(text)
    front = front_m.group(1) if front_m else ""
    body = text[front_m.end():] if front_m else text

    name_m = _NAME_RE.search(front)
    type_m = _TYPE_RE.search(front)
    desc_m = _DESC_RE.search(front)

    # Fallback: derive name from filename if no frontmatter
    name = name_m.group(1).strip() if name_m else path.stem.replace("_", "-")
    title = name.replace("-", " ").replace("_", " ").title()
    type_ = type_m.group(1).strip() if type_m else "other"
    summary = (desc_m.group(1).strip() if desc_m else body.strip().split("\n")[0])[:200]

    links = sorted(set(_LINK_RE.findall(body)))
    body_size = len(body)
    return {
        "file": path.name,
        "id": name,
        "name": name,
        "title": title,
        "type": type_,
        "summary": summary,
        "size": body_size,
        "links": links,
    }


def build_graph() -> dict[str, Any]:
    files = [p for p in sorted(MEMORY_DIR.glob("*.md")) if p.name not in SKIP]
    nodes_by_id: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []

    for p in files:
        meta = parse_file(p)
        if not meta:
            continue
        nodes_by_id[meta["id"]] = meta

    # Edges + stub nodes for dangling links
    for src_id, meta in list(nodes_by_id.items()):
        for tgt in meta["links"]:
            if tgt == src_id:
                continue  # ignore self-loops
            if tgt not in nodes_by_id:
                nodes_by_id[tgt] = {
                    "id": tgt, "name": tgt, "title": tgt,
                    "type": "stub", "summary": "(not written yet)",
                    "size": 0, "links": [],
                }
            edges.append({"source": src_id, "target": tgt})

    # Strip per-node link lists from output (now expressed as edges)
    # + tag each node with a recency status icon from file mtime
    import time
    now = time.time()
    mtimes: dict[str, float] = {}
    for p in MEMORY_DIR.glob("*.md"):
        if p.name not in SKIP:
            mtimes[p.name] = p.stat().st_mtime

    nodes = []
    for nid, n in nodes_by_id.items():
        mt = mtimes.get(n.get("file", ""), 0)
        if n["type"] == "stub":
            icon = "📝"
        elif mt == 0:
            icon = ""
        else:
            age_days = (now - mt) / 86400.0
            if age_days < 7:    icon = "🟢"
            elif age_days < 30: icon = "🟡"
            elif age_days < 90: icon = "🟠"
            else:               icon = "🔴"
        out = {k: v for k, v in n.items() if k != "links"}
        if icon:
            out["status_icon"] = icon
            out["mtime"] = mt
        nodes.append(out)

    type_counts: dict[str, int] = {}
    for n in nodes:
        type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1

    return {
        "nodes": sorted(nodes, key=lambda n: n["id"]),
        "edges": edges,
        "stats": {
            "files": len(files),
            "nodes": len(nodes),
            "edges": len(edges),
            "by_type": type_counts,
        },
    }


TYPE_ICON = {
    "user": "👤", "feedback": "⚠️", "project": "🗂", "reference": "🔗",
    "stub": "📝", "other": "📄",
}


def recency_label(mtime: float, now: float) -> str:
    age_days = (now - mtime) / 86400.0
    if age_days < 1: return "🟢 today"
    if age_days < 7: return "🟢 this week"
    if age_days < 30: return "🟡 this month"
    if age_days < 90: return "🟡 last 3mo"
    return "🔴 stale"


def render_markdown(g: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc).timestamp()
    nodes = g["nodes"]
    edges = g["edges"]
    by_id = {n["id"]: n for n in nodes}

    in_deg: dict[str, int] = defaultdict(int)
    out_deg: dict[str, int] = defaultdict(int)
    for e in edges:
        out_deg[e["source"]] += 1
        in_deg[e["target"]] += 1

    # Resolve files on disk for mtime + sizes
    mtime_by_file: dict[str, float] = {}
    for p in MEMORY_DIR.glob("*.md"):
        if p.name in SKIP: continue
        mtime_by_file[p.name] = p.stat().st_mtime

    lines: list[str] = []
    lines.append("# Memory digest")
    lines.append("")
    lines.append(f"Generated **{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}**.")
    lines.append("")
    s = g["stats"]
    by_type = " · ".join(f"{TYPE_ICON.get(k, '·')} {v} {k}" for k, v in sorted(s["by_type"].items(), key=lambda kv: -kv[1]))
    lines.append(f"**{s['nodes']} nodes** ({s['files']} files, {s['edges']} edges) — {by_type}")
    lines.append("")
    lines.append("Interactive graph: <https://teacher1.constantwrestling.cloud/memory-graph/>")
    lines.append("")

    # Hub nodes — most referenced
    hubs = sorted(nodes, key=lambda n: -in_deg.get(n["id"], 0))[:10]
    hubs = [n for n in hubs if in_deg.get(n["id"], 0) > 0]
    if hubs:
        lines.append("## 🌟 Hub nodes (most referenced)")
        lines.append("")
        for n in hubs:
            lines.append(f"- [[{n['id']}]] ← {in_deg[n['id']]} refs · {TYPE_ICON.get(n['type'], '·')} {n['type']}")
        lines.append("")

    # Stubs — wiki-links pointing to unwritten memories (TODO list)
    stubs = [n for n in nodes if n["type"] == "stub"]
    if stubs:
        lines.append(f"## 📝 Stubs ({len(stubs)}) — referenced but not yet written")
        lines.append("")
        for n in sorted(stubs, key=lambda x: -in_deg.get(x["id"], 0))[:15]:
            lines.append(f"- [[{n['id']}]] ← {in_deg.get(n['id'], 0)} refs")
        lines.append("")

    # Orphans — no edges in or out
    orphans = [n for n in nodes if n["type"] != "stub"
               and in_deg.get(n["id"], 0) == 0 and out_deg.get(n["id"], 0) == 0]
    if orphans:
        lines.append(f"## 🏝 Orphans ({len(orphans)}) — no links in or out")
        lines.append("")
        for n in sorted(orphans, key=lambda x: x["id"])[:15]:
            lines.append(f"- [[{n['id']}]] · {TYPE_ICON.get(n['type'], '·')} {n['type']}")
        if len(orphans) > 15:
            lines.append(f"- … and {len(orphans) - 15} more")
        lines.append("")

    # Recently edited
    recent = sorted(
        [(n, mtime_by_file.get(n.get("file", ""), 0)) for n in nodes if n.get("file")],
        key=lambda x: -x[1],
    )[:15]
    if recent:
        lines.append("## ⏱ Recently edited")
        lines.append("")
        for n, mt in recent:
            if mt == 0: continue
            when = datetime.fromtimestamp(mt, timezone.utc).strftime("%Y-%m-%d %H:%M")
            lines.append(f"- `{when}` [[{n['id']}]] · {recency_label(mt, now)}")
        lines.append("")

    # By type — full index
    lines.append("## 📚 Index by type")
    lines.append("")
    for t in sorted(s["by_type"].keys(), key=lambda k: -s["by_type"][k]):
        bucket = sorted([n for n in nodes if n["type"] == t], key=lambda x: x["id"])
        if not bucket: continue
        lines.append(f"### {TYPE_ICON.get(t, '·')} {t} ({len(bucket)})")
        lines.append("")
        for n in bucket:
            summary = (n.get("summary") or "").replace("\n", " ").strip()[:120]
            lines.append(f"- [[{n['id']}]] — {summary}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    graph = build_graph()
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    MD_OUT.write_text(render_markdown(graph), encoding="utf-8")
    print(f"wrote {OUT}: {graph['stats']}")
    print(f"wrote {MD_OUT}")


if __name__ == "__main__":
    main()
