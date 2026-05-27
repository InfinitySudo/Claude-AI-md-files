---
name: Daily-Driver Git Repos
description: Все репо Артёма с которыми я регулярно работаю — пути на VPS, GitHub origin, что внутри, какие сервисы запускают
type: project
originSessionId: 7ecab4cc-5fb7-4e8a-9ff9-8754cff466ae
---
GitHub org: **InfinitySudo** (private + public mix). Все репо клонированы в `/root/<name>/`. PAT-ы уже зашиты в `git remote` URL'ах — для push ничего отдельно настраивать не надо.

## Trading
| Repo | Path | GitHub | Что внутри | Live сервисы |
|---|---|---|---|---|
| **4BotsBybit-Trading** | `/root/4BotsBybit-Trading` | `InfinitySudo/4BotsBybit-Trading` | Главная торговая система — SignalBot, TradingBot, StrategySwitcher, ControlBot, dashboard_api_v3, GA optimizer | `bybit-signalbot`, `bybit-tradingbot`, `bybit-strategy-switcher`, `bybit-control-bot`, `dashboard-api`, `bybit-ga-weekly.timer`, claude-watchdog/hourly |
| **gerchik-trading-agent** | `/root/gerchik-trading-agent` | `InfinitySudo/gerchik-trading-agent` (private) | Phase 1 copy-trade Герчика: signals_bot @GTE_AI_TradingBot, copy_executor (ждёт API key sub-account), Phase 2 trigger | `gerchik-signals-bot`, `gerchik-phase2-trigger.timer` (executor — inactive до keys) |
| **4BotsBybit-Documentation** | `/root/4BotsBybit-Documentation` | (отдельный репо, доки/диаграммы) | Доки, схемы | — |

## Construction (TSA / OnTime)
| Repo | Path | GitHub | Что внутри | Live сервисы |
|---|---|---|---|---|
| **OnTime** | `/root/ontime` | `InfinitySudo/OnTime` | PWA для siding-компании TSA — checkin/timesheets, daily reports, projects, BOM, procurement, deliveries, service tasks, scoring, payroll, marketing video | `ontime-backend`, `ontime-tg-bot`, ontime-* timers (digests, OT watch, daily nudge, sync_legacy) |

## Voice / Education
| Repo | Path | GitHub | Что внутри | Live сервисы |
|---|---|---|---|---|
| **voice-tutor** | `/root/voice-tutor` | `InfinitySudo/voice-tutor` | TG голосовой собеседник (@AISmartFriendBot) + Mini App с continuous VAD/barge-in; voice.constantwrestling.cloud | `voice-tutor` (TG bot + web) |
| **wife-english-tutor** | `/root/wife-english-tutor` | `InfinitySudo/wife-english-tutor` | Жена A1-A2, correction-first `[FIX]...[/FIX]`. Разработка после fix voice-tutor | (не запущен) |
| **English-Teacher-CELPIP** | `/root/English-Teacher-CELPIP` | `InfinitySudo/English-Teacher-CELPIP` | 2 TG бота для CELPIP (Артём CLB 10, Лиля CLB 8); voice Whisper+Claude+TTS | `celpip_bot.py` (×2) |

## Email / Productivity
| Repo | Path | GitHub | Что внутри | Live сервисы |
|---|---|---|---|---|
| **emails-optimization** | `/root/emails-optimization` | `InfinitySudo/emails-optimization` | AI-секретарь для 6 email бизнесов; Gmail+Claude+TG; Артём (TEST_MODE) + Тим mirror, общий emails.db, agent-state по owner_chat_id; user-facing для Тима строго English | `emails-poller`, `emails-bot`, `emails-bot-tim`, emails-followups, emails-morning-digest |

## Tooling / Infra
| Repo | Path | GitHub | Что внутри | Live сервисы |
|---|---|---|---|---|
| **claude-telegram-bot** | `/root/claude-telegram-bot` | `InfinitySudo/Claude-Telegram-Bot` | TG бот с Claude API (voice+vision+tools+OAuth) — НЕ путать с openclaw-v3 | `claude-telegram-bot` |
| **solo_claude_bot** | `/root/solo_claude_bot` | `InfinitySudo/Solo_Claude_ru` | CLI для постинга в @solo_claude канал (build-in-public RU); 2 бота, venv, .env | `solo_claude_approve` |
| **Claude-AI-md-files** | `/root/Claude-AI-md-files` | (репозиторий с Markdown-checkpoint'ами) | Зеркало memory/checkpoint sessions (см. feedback_sync_memory_on_commit) | — (push only) |
| **Wrestling-Performance-Tracker** | `/root/Wrestling-Performance-Tracker` | (приватный) | Wrestling Tracker v2 PWA — multi-club norms, profile+socials, share card | wrestling-* services |

## Heavy compute (no daily commits, but used)
- **DeOldify**, **SadTalker**, **sadtalker_models** — photo restoration pipeline (см. project_photo_restoration). Запускается ad-hoc.
- **wife_photo_dance** — single-purpose script, не репо.

## Сессионные правила (важно)
- **Auto-push**: после каждого commit'а — сразу push (с 2026-05-02). См. feedback_auto_push_default.
- **Split commits**: независимые фичи = отдельные коммиты, не bundle. См. feedback_split_commits.
- **Sync to Claude-AI-md-files** на каждом push (если касается memory). См. feedback_sync_memory_on_commit.
- **CLAUDE.md в каждом репо** — читай первым. У 4BotsBybit-Trading + ontime есть production-rules (PLAN MODE для trading code, pytest перед commit).

## Quick `cd` по теме
- "трейдинг" → `/root/4BotsBybit-Trading`
- "Герчик" → `/root/gerchik-trading-agent`
- "OnTime / TSA / Тим / форман" → `/root/ontime`
- "voice / голос / @AISmartFriendBot" → `/root/voice-tutor`
- "жена English" → `/root/wife-english-tutor`
- "CELPIP" → `/root/English-Teacher-CELPIP`
- "Тим / emails" → `/root/emails-optimization`
- "канал @solo_claude" → `/root/solo_claude_bot`
