---
name: project-wrestling-uww-scoreboard
description: "UWW Heracles-style live scoreboard в wrestling app — count-down, P shot-clock, FALL/VSU/VPO, INJ-time, cast to TV"
metadata: 
  node_type: memory
  type: project
  originSessionId: c9d2b899-f272-4e25-b502-fa1e0f5284ca
---

С 2026-05-19 (commits c9ba5db→c3a0e61) wrestling app имеет полноценное UWW-табло для спаррингов. Live на `https://constantwrestling.cloud/scoreboard/:mid`.

## Архитектура

**Backend (`backend/main.py`)**
- Таблица `tournament_matches` хранит: `match_format` (free|kids|senior), `period_duration_sec` (default 180), `break_duration_sec` (30), `period_num`, `mat_time_sec`, `timer_running`, `timer_started_at`, `ended_at`, `result_code` (FALL/VSU/VPO/VPO1/VFA/DSQ), плюс `round_label`/`discipline`/`age_group`/`weight_class`.
- Таблица `match_events`: каждое действие (point/caution/passivity_award/period_start/end/fall) с `athlete_side` (A|B), `points`, `period_num`, `mat_time_sec`, `recorded_by`, `created_at`. Используется для timeline и live score aggregation.
- Endpoints: `GET /api/matches/{mid}` (детали + score_a/b), `GET /api/matches/{mid}/events`, `POST /api/matches/{mid}/events`, `DELETE /api/matches/{mid}/events/last` (undo), `PATCH /api/matches/{mid}/meta`. Все club-scoped (anyone in host club может видеть), writes требуют coach.

**Frontend (`src/components/UWWScoreboard.jsx` + `src/pages/ScoreboardPage.jsx`)**
- Route `/scoreboard/:mid?display=1` вне Layout (без nav, для ТВ).
- One-click pairing внутри спарринга (`TournamentsPage.jsx` → `UWWMatchPanel`): тапнул борца → слот A → второй тап → B → match создаётся + scoreboard открывается.
- Cast to TV: иконка → `window.open('/scoreboard/{mid}?display=1', ...)`. Sync через `BroadcastChannel(uww-match-{mid})` + 1.5s polling fallback.

## Правила UWW реализованные

- **Format select** (top header): Free (count-up) / Kids 2×2 / Senior 2×3.
- **Count-down таймер** = `period_duration_sec - elapsed`. По умолчанию senior (3:00).
- **30s break** между периодами — локальный countdown, потом auto-flip на P2 / 0:00.
- **Auto-end** после P2 hit 0:00 (или последнего period_num >=2).
- **P (passivity)** → starts 30s shot-clock against opponent. Side показывает yellow `Shot-clock Ns`. Если оппонент scoreит — clock cancels. Если 30s истекает — opponent получает +1 (`passivity_award` event). P×N счётчик per side в шапке стороны.
- **FALL ⬅ / ➡ FALL** — pin button, end с result_code='FALL', winner = chosen side.
- **Auto tech-superiority**: |scoreA−scoreB| ≥ 8 (GR) / ≥ 10 (FS/WW) + противник на 0 → end с VSU.
- **INJ** — 2-минутный injury countdown (red), main timer паузится, "End injury" кнопка.
- **Result codes**: FALL / VSU / VPO (loser scored) / VPO1 (loser 0) / VFA / DSQ. Вычисляются в `classifyResult()`.
- **Undo** — DELETE last event (откатывает score).

## Time-zone fix

FastAPI сериализует naive datetime без TZ-маркера. Browser `new Date(naive)` парсит как local, ломает Math.max(0, delta) на сервере UTC. Frontend в `elapsedSec` добавляет `Z` если нет TZ. Backend пишет `timer_started_at = NOW() AT TIME ZONE 'UTC'` чтобы быть устойчивым к смене Postgres tz. Проверено E2E на 9 timezone (Calgary..Sydney).

## TDZ gotcha

`useEffect` deps array читается синхронно при render. Если effect ссылается на `metaMut` (useMutation) который объявлен ниже — в минифицированном bundle получаем "Cannot access 'D' before initialization". Все три эффекта (auto-pause, break-arm, break-tick, tech-sup, auto-end) живут ПОСЛЕ объявления metaMut.

## Связано
- [[project_wrestling_v2]] — общий контекст
- [[project_wrestling_pill_nav]] — bottom-nav
- [[feedback_react_hooks_order]] — TDZ pattern
