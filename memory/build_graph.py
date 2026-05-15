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
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
MEMORY_DIR = ROOT
OUT = MEMORY_DIR / "graph.json"

# Skip non-memory files like the index and this script.
SKIP = {"MEMORY.md", "build_graph.py", "graph.html", "graph.json"}

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
    nodes = []
    for nid, n in nodes_by_id.items():
        nodes.append({k: v for k, v in n.items() if k != "links"})

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


def main() -> None:
    graph = build_graph()
    OUT.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {OUT}: {graph['stats']}")


if __name__ == "__main__":
    main()
