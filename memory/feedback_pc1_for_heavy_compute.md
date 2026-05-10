---
name: PC1 для тяжёлого compute
description: Любая тяжёлая нагрузка (ML training, batch-обработка, GA, рендеринг, photo restoration) идёт на ПК1 (RTX 3090, Tailscale 100.99.211.123, ssh user=tkach) — VPS оставляем для live-сервисов
type: feedback
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
Rule: Всё тяжёлое и параллелизуемое запускать на ПК1, забыть про мощности VPS. Если задачу можно выполнить за минуты на ПК1 GPU/CPU — НЕ запускать её на VPS даже если код там уже есть.

**Why:** VPS должен оставаться freed for live trading bots, dashboard, signal_bot, real-time pollers. Любой долгий compute на VPS конкурирует с торговлей за CPU и память. ПК1 простаивает 23h/24, имеет RTX 3090 + 64GB RAM, через Tailscale доступен с задержкой <10ms. Артём явно попросил 2026-05-08: «всё что тяжёлое и его можно быстро сделать на моём ПК с помощью моего железа делаем на моём ПК всегда, забиваем про мощности VPS».

**How to apply:**
- GA optimizer — уже на ПК1 через `/api/ga/run target=pc1` (см. project_ga_gpu_migration)
- ML тренировка (XGBoost meta-labeler, FinRL agents и т.п.) — на ПК1, синхронизация модели обратно на VPS scp'ом
- Photo restoration (GFPGAN/LaMa/DeOldify) — на ПК1 (project_photo_restoration кандидат на миграцию)
- Большие backtests, parameter sweeps, simulation runs — на ПК1
- Любая задача >5 минут CPU на VPS — оценить миграцию на ПК1
- Шаблон вызова: `ssh tkach@100.99.211.123 'cd C:\path && venv\Scripts\python.exe -u script.py'`
- Файлы синхронизировать через `scp` (не git) — VPS остаётся source-of-truth для кода
- Если ПК1 недоступен (sleep/Tailscale down) — fallback на VPS только для critical path; non-critical откладывать
- Исключение: задачи которые требуют доступа к prod-DB/bybit-state с минимальной задержкой остаются на VPS
