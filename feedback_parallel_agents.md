---
name: Parallel agents on the VPS
description: Artem may run other AI agents (OpenClaw, etc.) in parallel with Claude Code on the same VPS — check before destructive ops
type: feedback
originSessionId: 3c5941a8-e584-46d0-a8e0-72ab5293d0b2
---
Before running destructive operations on the VPS (rm -rf, killing processes, stopping services), check whether a parallel AI agent is active and working in the target area. Specifically:
- `systemctl --user is-active openclaw-gateway` — OpenClaw is a node.js CLI agent Artem has installed. Its sessions live in `/root/.openclaw/agents/main/sessions/*.jsonl`.
- `ps auxww | grep -iE "openclaw|claude"` — look for any live harness processes.
- If a parallel agent is working in the directory you're about to delete, it may have started background processes from there (like api_simple_8003.py on 2026-04-10). Killing those processes out from under the other agent breaks its work.

**Why:** On 2026-04-10 I was about to archive/delete `/root/4botsBybit-production`. An OpenClaw session (d30f7bc0) was actively using that directory and had just spawned `api_simple_8003.py` on port 8003. Had I deleted blindly, I would have killed a live process belonging to another agent session and destroyed its work context.

**How to apply:** When starting invasive cleanup (file deletion, service shutdown, process kills), do a parallel-agent scan first. If another agent is active in the target area, pause and ask Artem whether to stop the other agent first, or to skip the cleanup and move on.
