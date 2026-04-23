---
name: GA subprocess must detach (start_new_session=True)
description: Long-running subprocess.Popen children of dashboard-api die on systemctl restart unless they leave the cgroup
type: feedback
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
On 2026-04-22 a 7-hour GA prod run (PID 2185750) was silently killed
at gen ~2-3 when `systemctl restart dashboard-api.service` was issued
for an unrelated WR fix. Cause: subprocess.Popen children inherit the
systemd unit's cgroup; default `KillMode=control-group` SIGTERMs every
cgroup member on restart. The GA was a child of dashboard-api → it
died with it.

The aftermath looked like a successful run from the API's view:
`/api/ga/status` saw the PID was gone and flipped `state=completed`.
But `completed_at=None` and `ga_results_latest.json` mtime unchanged
were the real tells.

**Fix:** pass `start_new_session=True` to `subprocess.Popen` for any
long-running child that should outlive service restarts. This puts
the child in its OWN session/process group so the cgroup kill leaves
it alone.

Verified by checking PGIDs:
```
dashboard-api PGID=X
GA            PGID=Y   # different = detached, survives restarts
```

**Why:** Without detach, any stat-fix iteration on dashboard code
during a multi-hour GA run accidentally cancels it. Wasted compute
and wasted operator time.

**How to apply:** `subprocess.Popen(..., start_new_session=True)` for:
- GA optimizer
- ga_notify_on_complete watcher
- anything else launched from dashboard-api or other systemd-managed
  services that takes > a few minutes.

**Detection:** Long-running subprocess that ended without writing its
expected output file → check if its parent service was restarted
during the run. mtime of the log file usually pins the time of
death.
