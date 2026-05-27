---
name: PC1 ssh→PowerShell→python детач — обязательно WMI Win32_Process.Create + per-PID лог-файлы
description: Запоминания из 2026-05-08 при wiring PC1 GPU GA: 5 каскадных Windows-quirks; решение через WMI + per-PID log filenames + utf-8 reconfigure
type: feedback
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
Rule: при ssh-инициированных background-Python процессах на ПК1 (Windows 11) **НЕ использовать** PowerShell `Start-Process` с redirect — использовать **WMI `Win32_Process.Create`**. Логи python должны идти в **per-PID файлы** (`ga_run_<pid>.log`), не в фиксированное имя.

**Why:** На сессии 2026-05-08 наткнулся на 5 каскадных багов когда поднимал `/api/ga/run target=pc1`:
1. PowerShell `Start-Process -ArgumentList` принимает строку как ОДИН argv slot — нужен `@()` массив
2. `cd C:/...` в cmd через ssh не находит `venv/Scripts/python.exe` — нужно backslash
3. Windows Defender держит handle на `ga_run.log` после exit процесса → следующий запуск падает с PermissionError. Исправление — per-PID имена файлов
4. **Главное:** `Start-Process` через ssh-сессию убивает python после kline-load когда ssh закрывается (console-attached child + CTRL_BREAK on session close). WMI спавнит через WMI service — fully detached
5. PowerShell tail в poller'е возвращал cp1252 BOM байты которые ломали `subprocess.run(text=True)` без `errors='replace'`

**How to apply:**
- В `scripts/gpu/run_ga.ps1` уже шаблон: WMI Create + поиск python pid через `ga_run_*.log` filename match
- В `scripts/pc1_status_poller.py`: `subprocess.run(..., encoding='utf-8', errors='replace')`
- Любой долгий python process на ПК1 через ssh: использовать те же patterns или risk silent kill
- Foreground ssh-вызовы (типа `ssh tkach@... 'python.exe ...'`) работают нормально — детач-проблема только при background
- Для VPS-only python скриптов всё работает обычным subprocess.run / systemd-run
