---
name: Long subprocess from dashboard-api must use systemd-run, NOT start_new_session
description: cgroup-kill on dashboard-api restart nukes every child. start_new_session=True does NOT help. Use systemd-run --unit --slice.
type: feedback
originSessionId: 140ba16f-5e2e-494a-890b-d8dc107dddde
---
Любой долгоживущий subprocess (GA optimizer, notify watcher, и т.п.)
запускать только как transient systemd unit через `systemd-run`.
Прежний «фикс» с `subprocess.Popen(..., start_new_session=True)` —
**недостаточен**. Он меняет session/PGID, но systemd отслеживает
потомков через **cgroup членство**, а не через PGID. При
`systemctl restart dashboard-api` (у сервиса `KillMode=control-group`)
systemd прибивает ВСЕ процессы в его cgroup, детач по session тут
не спасает.

Подтверждено двумя потерянными прогонами:
- 2026-04-22 ~20:10 UTC: 7-часовой GA прибит при рестарте dashboard-api
  (это и породило миф про start_new_session)
- 2026-04-22 ~23:45 UTC: GA #2 + notify watcher оба умерли синхронно,
  хотя оба были с `start_new_session=True`. Ни OOM, ни kern panic —
  cgroup kill при очередном рестарте dashboard-api.

**Правильный фикс (применён в `src/dashboard_api_v3.py:1598`):**
```python
subprocess.run([
    'systemd-run',
    '--unit', f'ga-optimizer-{int(time.time())}.service',
    '--slice', 'background.slice',
    '--collect',
    '--property', f'StandardOutput=append:{log_path}',
    '--property', 'StandardError=inherit',
    '--property', f'WorkingDirectory={cwd}',
    '--property', 'Nice=10',
    sys.executable, '-u',  # ← unbuffered, иначе per-gen prints теряются
    script_path, *args,
], check=True, timeout=15, capture_output=True)
# Достать PID:
pid = int(subprocess.run(['systemctl', 'show', unit, '-p', 'MainPID',
                          '--value'], capture_output=True, text=True).stdout.strip())
```

Ключевые моменты:
1. `--unit=name.service` → отдельный transient unit, свой cgroup
2. `--slice=background.slice` → вне system.slice, не трогается рестартом
3. `--collect` → unit самоудаляется после завершения
4. `python3 -u` обязательно, иначе DEAP per-gen прогресс сидит в block
   buffer и не попадает в лог до конца прогона — диагностировать
   невозможно
5. Записать в ga_status.json **и** pid, **и** unit name — по unit
   можно потом `systemctl show`/`stop` даже после рестарта dashboard

**Why:** без этого каждый dashboard-хотфикс кансилит долгий прогон;
первый фикс (start_new_session) создал ложное чувство безопасности.

**How to apply:** для любого Popen'а из dashboard-api / systemd-сервиса
с ожидаемой длительностью > ~5 минут — разворачивать через systemd-run.
Проверять работу изоляции так:
```
systemctl restart dashboard-api
ps -p <ga-pid>   # должен остаться жив
```
