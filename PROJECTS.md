# Projects digest

Generated **2026-05-14T20:30:49+00:00** — load this at the start of a new session for a 30-second overview.

**16 projects** — 🟢 9 live · 🟡 4 dev · 🔴 3 paused

Interactive graph: <https://teacher1.constantwrestling.cloud/projects-graph/>

## 🟢 Live (9)

### [voice-tutor](https://github.com/InfinitySudo/voice-tutor)

> Voice-first AI tutor in Telegram: 5-lesson generated mini-courses on any topic, hands-free Whisper+Claude+TTS loop with memory between lessons

- **Local:** `/root/voice-tutor` (1906.2 MB) · CLAUDE.md ✓
- **Lang:** Python · **Last push:** 2026-05-14 · **Vis:** PRIVATE
- **Services:** `son-french-tutor-digest`✗, `son-french-tutor-reminder`✗, `son-french-tutor-web`✓, `son-french-tutor`✓, `voice-tutor-web`✓, `voice-tutor`✓, `wife-english-tutor-digest`✗, `wife-english-tutor-reminder`✗, `wife-english-tutor-web`✓, `wife-english-tutor`✓
- **Hosts:** —
- **DB:** `data/tutor.db`
- **.env keys:** `OPENAI_API_KEY`, `VT_ALLOWED_USER_IDS`, `VT_BOT_TOKEN`, `VT_DB_PATH`, `VT_DEFAULT_LANGUAGE`, `VT_DEFAULT_LEVEL`, `VT_LLM_BACKEND`, `VT_LOCAL_LLM_MAX_TOKENS`, `VT_LOCAL_LLM_MODEL`, `VT_LOCAL_LLM_NUM_CTX`…
- **Memory (19):** [[PROJECTS]], [[feedback_avatar_video_calibration]], [[feedback_oauth_force_refresh]], [[feedback_oauth_rate_limits]], [[feedback_tutor_tts_wiring]], [[feedback_voice_chain_autoplay]], [[feedback_voice_tutor_oauth_500]], [[project_git_repos_daily]]…

### [son-french-tutor](https://github.com/InfinitySudo/son-french-tutor)

> AI French tutor for Andrii (Artem's son, A1-A2) — Telegram bot + PWA mini app

- **Local:** `/root/son-french-tutor` (24.5 MB)
- **Lang:** Python · **Last push:** 2026-05-14 · **Vis:** PRIVATE
- **Services:** `son-french-tutor-digest`✗, `son-french-tutor-reminder`✗, `son-french-tutor-web`✓, `son-french-tutor`✓
- **Hosts:** —
- **DB:** `data/tutor.db`, `db/sft.db`
- **.env keys:** `OPENAI_API_KEY`, `WET_ALLOWED_TG_IDS`, `WET_DB`, `WET_DEFAULT_LEVEL`, `WET_DEV_NAME`, `WET_DEV_TG_ID`, `WET_LIPSYNC_TIMEOUT`, `WET_LOCAL_LLM_MODEL`, `WET_LOCAL_LLM_URL`, `WET_READ_APP_URL`…
- **Memory (18):** [[PROJECTS]], [[feedback_avatar_video_calibration]], [[feedback_billable_service_close]], [[feedback_email_register_stub_upgrade]], [[feedback_multi_fix_per_sentence]], [[feedback_oauth_force_refresh]], [[feedback_salaried_roles_excluded_from_payroll]], [[feedback_tg_persistent_keyboard]]…

### [wife-english-tutor](https://github.com/InfinitySudo/wife-english-tutor)

- **Local:** `/root/wife-english-tutor` (41.3 MB)
- **Lang:** Python · **Last push:** 2026-05-14 · **Vis:** PRIVATE
- **Services:** `wife-english-tutor-digest`✗, `wife-english-tutor-reminder`✗, `wife-english-tutor-web`✓, `wife-english-tutor`✓
- **Hosts:** —
- **DB:** `data/tutor.db`, `db/wet.db`
- **.env keys:** `OPENAI_API_KEY`, `WET_ALLOWED_TG_IDS`, `WET_DB`, `WET_DEFAULT_LEVEL`, `WET_DEV_NAME`, `WET_DEV_TG_ID`, `WET_LOCAL_LLM_MODEL`, `WET_LOCAL_LLM_URL`, `WET_READ_APP_URL`, `WET_STT_BASE_URL`…
- **Memory (16):** [[PROJECTS]], [[feedback_multi_fix_per_sentence]], [[feedback_oauth_force_refresh]], [[feedback_tg_persistent_keyboard]], [[feedback_tutor_tts_wiring]], [[feedback_voice_tutor_oauth_500]], [[project_git_repos_daily]], [[project_session_2026_05_14_emails_perf_photo]]…

### [emails-optimization](https://github.com/InfinitySudo/emails-optimization)

- **Local:** `/root/emails-optimization` (981.9 MB)
- **Lang:** Python · **Last push:** 2026-05-14 · **Vis:** PRIVATE
- **Services:** `emails-bot-tim`✓, `emails-bot`✓, `emails-followups`✗, `emails-morning-digest`✗, `emails-poller`✓
- **Hosts:** —
- **DB:** `emails.db`
- **.env keys:** `ANTHROPIC_API_KEY`, `BUSINESS_NAME`, `BUSINESS_TONE`, `EMAILS_STT_BASE_URL_1`, `EMAILS_STT_BASE_URL_2`, `EMAILS_STT_PK_HEAD_START`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `NOTIFY_CUTOFF_HOURS`, `OPENAI_API_KEY`…
- **Memory (141):** [[PROJECTS]], [[feedback_action_type_no_names]], [[feedback_billable_hours_dedup]], [[feedback_bybit_ws_keepalive]], [[feedback_dashboard_first_workflow]], [[feedback_dashboard_utc]], [[feedback_dashboard_v1_v2]], [[feedback_dashboard_view_lock]]…

### [4BotsBybit-Trading](https://github.com/InfinitySudo/4BotsBybit-Trading)

> Advanced ByBit Trading Bot with Signal Detection, Risk Management, VARIANT 3 (ATR+Volume), Paper/Real Trading, PostgreSQL Integration

- **Local:** `/root/4BotsBybit-Trading` (53788.0 MB) · CLAUDE.md ✓
- **Lang:** Python · **Last push:** 2026-05-13 · **Vis:** PRIVATE
- **Services:** `bybit-anomaly-detector`✗, `bybit-auto-blacklist`✗, `bybit-claude-hourly`✗, `bybit-claude-watchdog`✗, `bybit-control-bot`✓, `bybit-daily-summary`✗, `bybit-db-backup`✗, `bybit-divergence-monitor`✗, `bybit-ga-weekly`✗, `bybit-meta-retrain`✗, `bybit-risk-officer`✗, `bybit-signalbot`✓, `bybit-strategy-switcher`✓, `bybit-tradingbot`✓, `dashboard-api`✓
- **Hosts:** —
- **DB:** `trading_data.db`, `paper_trading.db`, `data/trading_paper.db`, `data/paper_trading_v3.db`, `data/trading_bot.db`
- **.env keys:** `BYBIT_API_KEY`, `BYBIT_API_SECRET`, `BYBIT_GERCHIK_API_KEY`, `BYBIT_GERCHIK_API_SECRET`, `BYBIT_TESTNET`, `CLAUDE_BRIDGE_BOT_TOKEN`, `DB_HOST`, `DB_NAME`, `DB_PASSWORD`, `DB_PORT`…
- **Memory (46):** [[PROJECTS]], [[feedback_auto_push_default]], [[feedback_be_on_real]], [[feedback_bybit_ws_keepalive]], [[feedback_controlbot_shutdown_hook]], [[feedback_dashboard_v1_v2]], [[feedback_dashboard_view_lock]], [[feedback_dd_guard_paper_skip]]…

### [OnTime](https://github.com/InfinitySudo/OnTime)

> OnTime — PWA project deadline & hours tracker for siding crews (TSA)

- **Local:** `/root/ontime` (8198.4 MB) · CLAUDE.md ✓
- **Lang:** Python · **Last push:** 2026-05-12 · **Vis:** PRIVATE
- **Services:** `invoice-sync`✗, `ocr-followup`✗, `ontime-api`✓, `ontime-bot`✓, `roofmart-weekly`✗
- **Hosts:** `ontime.management`, `teacher1.constantwrestling.cloud`
- **DB:** `tsa.db`, `ontime.db`, `backend/tsa.db`, `backend/ontime.db`, `migration/legacy.db`
- **Memory (68):** [[PROJECTS]], [[feedback_billable_hours_dedup]], [[feedback_dayoff_silence]], [[feedback_email_register_stub_upgrade]], [[feedback_estimating_no_api]], [[feedback_fastapi_route_order]], [[feedback_legacy_db_safety]], [[feedback_narrative_before_details]]…

### [gerchik-trading-agent](https://github.com/InfinitySudo/gerchik-trading-agent)

> AI trading agent based on Alexander Gerchik's price-action methodology (levels, RR>=3, MM). Self-learning loop with rule engine + ML scorer + LLM reflector. Companion to InfinitySudo/4BotsBybit-Trading (volume-spike). Shared Bybit account, symbol pool split.

- **Local:** `/root/gerchik-trading-agent` (0.9 MB)
- **Lang:** Python · **Last push:** 2026-05-11 · **Vis:** PRIVATE
- **Services:** `gerchik-agent`✓, `gerchik-copy-executor`✓, `gerchik-daily-snapshot`✗, `gerchik-evening-summary`✗, `gerchik-gap-cron`✗, `gerchik-health`✗, `gerchik-phase2-trigger`✗, `gerchik-signals-bot`✓, `gerchik-weekly-reflector`✗
- **Hosts:** —
- **.env keys:** `BYBIT_API_KEY`, `BYBIT_API_SECRET`, `BYBIT_GERCHIK_API_KEY`, `BYBIT_GERCHIK_API_SECRET`, `BYBIT_TESTNET`, `CLAUDE_BRIDGE_BOT_TOKEN`, `DB_HOST`, `DB_NAME`, `DB_PASSWORD`, `DB_PORT`…
- **Memory (7):** [[PROJECTS]], [[feedback_bybit_empty_result_truthy_trap]], [[feedback_gerchik_leverage_88_too_high]], [[project_bybit_v5_open_close_knowledge]], [[project_gerchik_bot]], [[project_gerchik_copy_phase1]], [[project_git_repos_daily]]

### [Wrestling-Performance-Tracker](https://github.com/InfinitySudo/Wrestling-Performance-Tracker)

> Wrestling Performance Tracker

- **Local:** `/root/Wrestling-Performance-Tracker` (235.4 MB) · CLAUDE.md ✓
- **Lang:** JavaScript · **Last push:** 2026-05-09 · **Vis:** PRIVATE
- **Services:** `wrestling-api`✓
- **Hosts:** `_`, `constantwrestling.cloud`
- **Memory (17):** [[PROJECTS]], [[feedback_narrative_before_details]], [[feedback_wrestling_norm_attempts]], [[project_10k_strategy]], [[project_deploy_state]], [[project_git_repos_daily]], [[project_mobile_dev_workflow]], [[project_son_french_tutor]]…

### [Claude-Telegram-Bot](https://github.com/InfinitySudo/Claude-Telegram-Bot)

> Personal Claude Telegram bot: voice + vision + smart model routing + tool use (Haiku/Sonnet/Opus) over Claude Code OAuth

- **Local:** `/root/claude-telegram-bot` (51.3 MB) · CLAUDE.md ✓
- **Lang:** Python · **Last push:** 2026-05-02 · **Vis:** PRIVATE
- **Services:** `claude-telegram-bot`✓
- **Hosts:** —
- **Memory (8):** [[PROJECTS]], [[feedback_oauth_rate_limits]], [[feedback_voice_tutor_oauth_500]], [[project_claude_telegram_bot]], [[project_deploy_state]], [[project_git_repos_daily]], [[project_hourly_supervisor]], [[project_mobile_dev_workflow]]

## 🟡 Dev (4)

### [graph-system](https://github.com/InfinitySudo/graph-system)

> Knowledge graphs for memory, trading, tutors, OnTime — start with memory_graph

- **Local:** `/root/graph-system` (0.7 MB)
- **Lang:** HTML · **Last push:** 2026-05-14 · **Vis:** PRIVATE
- **Services:** `graph-rebuild`✗
- **Hosts:** —
- **Memory (1):** [[PROJECTS]]

### [Claude-AI-md-files](https://github.com/InfinitySudo/Claude-AI-md-files)

> 4BotsBybit Trading Bot - Complete Project Documentation & Analysis

- **Local:** `/root/Claude-AI-md-files` (1.1 MB) · CLAUDE.md ✓
- **Lang:** HTML · **Last push:** 2026-05-14 · **Vis:** PUBLIC
- **Services:** `memory-sync`✗
- **Hosts:** —
- **Memory (5):** [[PROJECTS]], [[feedback_auto_push_default]], [[feedback_sync_memory_on_commit]], [[project_git_repos_daily]], [[project_mobile_dev_workflow]]

### [Solo_Claude_ru](https://github.com/InfinitySudo/Solo_Claude_ru)

> Bilingual draft-to-publish pipeline for @solo_claude (RU) and @Solo_Claude_en (EN) TG channels. Build in public, automated daily post generator, inline-button approval flow.

- **Local:** `—` (— MB)
- **Lang:** Python · **Last push:** 2026-05-02 · **Vis:** PRIVATE
- **Services:** —
- **Hosts:** `_`, `constantwrestling.cloud`, `ontime.management`, `son.constantwrestling.cloud`, `teacher1.constantwrestling.cloud`, `voice.constantwrestling.cloud`
- **Memory (10):** [[PROJECTS]], [[feedback_narrative_before_details]], [[feedback_oauth_rate_limits]], [[project_deploy_state]], [[project_git_repos_daily]], [[project_gpu_homelab_plan]], [[project_mobile_dev_workflow]], [[project_solo_claude_bot]]…

### [English-Teacher-CELPIP](https://github.com/InfinitySudo/English-Teacher-CELPIP)

> English teacher / CELPIP prep app

- **Local:** `/root/English-Teacher-CELPIP` (73.2 MB) · CLAUDE.md ✓
- **Lang:** Python · **Last push:** 2026-05-02 · **Vis:** PRIVATE
- **Services:** `celpip-bot@`✗, `celpip-reminder@`✗
- **Hosts:** —
- **DB:** `data/celpip_liliia.db`, `data/celpip_artem.db`
- **.env keys:** `CELPIP_BOT_TOKEN`, `CELPIP_DB_PATH`, `CELPIP_EXAM_DATE`, `CELPIP_OWNER_ID`, `CELPIP_TARGET_CLB`, `CELPIP_TTS_VOICE`, `CELPIP_UI_LANG`, `CELPIP_USER_NAME`, `OPENAI_API_KEY`
- **Memory (11):** [[PROJECTS]], [[feedback_multi_fix_per_sentence]], [[feedback_oauth_rate_limits]], [[feedback_telegram_keyboard_emoji]], [[feedback_voice_tutor_oauth_500]], [[project_claude_telegram_bot]], [[project_deploy_state]], [[project_git_repos_daily]]…

## 🔴 Paused (3)

### [OpenClaw-v3](https://github.com/InfinitySudo/OpenClaw-v3)

> OpenClaw v3 - Telegram Bot

- **Local:** `—` (— MB)
- **Lang:** Python · **Last push:** 2026-04-08 · **Vis:** PRIVATE
- **Services:** —
- **Hosts:** `_`, `constantwrestling.cloud`, `ontime.management`, `son.constantwrestling.cloud`, `teacher1.constantwrestling.cloud`, `voice.constantwrestling.cloud`
- **Memory (3):** [[PROJECTS]], [[project_claude_telegram_bot]], [[project_git_repos_daily]]

### [my-openclaw-brain](https://github.com/InfinitySudo/my-openclaw-brain)

- **Local:** `—` (— MB)
- **Lang:** — · **Last push:** 2026-04-08 · **Vis:** PRIVATE
- **Services:** —
- **Hosts:** `_`, `constantwrestling.cloud`, `ontime.management`, `son.constantwrestling.cloud`, `teacher1.constantwrestling.cloud`, `voice.constantwrestling.cloud`
- **Memory (1):** [[PROJECTS]]

### [bybit-trading-bot](https://github.com/InfinitySudo/bybit-trading-bot)

> ByBit Trading Bot 

- **Local:** `—` (— MB)
- **Lang:** Python · **Last push:** 2026-03-15 · **Vis:** PRIVATE
- **Services:** —
- **Hosts:** `_`, `constantwrestling.cloud`, `ontime.management`, `son.constantwrestling.cloud`, `teacher1.constantwrestling.cloud`, `voice.constantwrestling.cloud`
- **Memory (1):** [[PROJECTS]]
