---
name: Dashboard API startup gotchas
description: Two issues found when dashboard_api_v3.py wasn't serving data — env pollution and nginx double config
type: feedback
originSessionId: d03703be-ddc9-425c-a090-1f7f84b164e5
---
1. **Don't start dashboard_api_v3.py from a session where pytest set test env vars** — env_config reads os.environ first, .env second. If BYBIT_API_KEY is already set to 'test_key' in the process env, .env won't override it. Start with clean env: `env -i HOME=/root PATH=$PATH PYTHONPATH=... python3 src/dashboard_api_v3.py`

**Why:** Bybit balance returned 0.0 because test credentials were used instead of real ones.

**How to apply:** When starting bot processes manually, ensure no stale test env vars. In production use the start script or docker-compose which have clean environments.

2. **Nginx had two conflicting server blocks on :8080** — `sites-enabled/dashboard` (proxy to :8000) and `conf.d/default.conf` (proxy to :8003/api_stable.py). The second one won, routing API calls to the old empty API.

**Why:** Dashboard showed all zeros despite dashboard_api_v3.py running correctly on :8000.

**How to apply:** Old `conf.d/default.conf` was renamed to `.bak`. Only `sites-enabled/dashboard` → :8000 remains active.
