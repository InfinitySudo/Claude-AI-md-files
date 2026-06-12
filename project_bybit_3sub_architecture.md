---
name: bybit-3-sub-architecture
description: "Bybit account isolation after 2026-05-15 migration — 3 sub-accounts each isolated to one bot (TradingBot/Gerchik copy/AI-agent). UIDs, env var slots, .env symlink trap."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4549af2c-3ca5-42b1-8cf2-f9e95b8aeb3c
---

С 2026-05-15 торговля разнесена на 3 sub-аккаунта Bybit (изоляция margin и orphan-tracking):

| UID | Sub | Bot | Env vars |
|-----|-----|-----|----------|
| 563399107 | sub1 | TradingBot (main_bot_v3) | `BYBIT_API_KEY` / `BYBIT_API_SECRET` |
| 563470305 | sub2 | Gerchik copy-executor + signals_bot | `BYBIT_GERCHIK_API_KEY` / `BYBIT_GERCHIK_API_SECRET` |
| 539929753 | sub3 | AI-agent (gerchik-trading-agent main) | `BYBIT_AI_AGENT_API_KEY` / `BYBIT_AI_AGENT_API_SECRET` |
| 567356487 | sub4 | **Real trading (Trader F)** — note "Trader_F", ~$100 | `BYBIT_REAL_API_KEY` / `BYBIT_REAL_API_SECRET` |

**2026-06-05 — добавлен sub4 для real-трейдинга (Trader F).** Глобальный `real_executor` (`main_bot_v3.py:127`) и live-чтения дашборда (`_bybit_signed_get`) теперь на `BYBIT_REAL_*` (фоллбэк на sub1 если не задано). Commit `3c8b7b7`. ⚠ Это НЕ per-trader routing: `real_executor` один, поэтому ЛЮБОЙ real-трейдер идёт на sub4. Защита от коллизии 2-х real на sub4 = `max_concurrent_real=1` (выставлен). Полная изоляция (F на sub4, C на sub1 одновременно) требует per-trader executor routing — отложено. sub4 добавлен в `_BYBIT_SUBS` (dashboard wallets-all). Детали: [[project-session-2026-06-05-real-sl-promoter]].

Старые отжившие аккаунты:
- uid 539929753 раньше был общим для TradingBot+AI-agent (один кошелёк, конфликт margin) — теперь чисто AI-agent через отдельный sub3 ключ.
- uid 100548867 — старый Gerchik sub, больше не используется (баланс перенести руками в UI и удалить старые API ключи Htba1U/NVFHin).

**Why:** До миграции TradingBot и AI-agent делили один кошелёк → risk_manager TradingBot'a видел позы AI-agent'a как orphan и пытался их сопровождать через dust-sweep. После — каждый бот изолирован, никакого cross-contamination.

**Dashboard Stream-labels (2026-05-16, см. [[feedback-streams-a-b-c-terminology]]):**
- 📥 **Stream A — Gerchik copy** = sub2 (DB: `gerchik_copy_trades`)
- 🤖 **Stream B — AI-agent** = sub3 (DB: `gerchik_trades`; UI читает Bybit-truth напрямую через закрытые-pnl API)
- 💰 **Main TradingBot (sub1)** = sub1 (DB: `real_trades`) — было "Stream C — our agent", переименовано

**Pyramid fix 2026-05-16 (sub3 only):** см. [[project-pyramid-fix-gerchik-trading-agent]]. До 2026-05-16 коммита `dbea126` AI-agent inflated PnL 3.4× (XRPUSDT incident).

**How to apply:**
- `/root/gerchik-trading-agent/src/env_config.py:bybit_creds()` читает `BYBIT_AI_AGENT_API_KEY` с fallback на `BYBIT_API_KEY` — не сломать этот fallback.
- IP whitelist на всех 3 ключах: `187.77.148.44`, `46.8.232.182` (Артём диктовал при создании).
- Все 3 sub имеют `unified: 0` (classic, не UTA). Linear USDT perp работает, но `accountType=CONTRACT` для wallet может быть нужен на отдельных эндпоинтах.
- Permissions на всех: ContractTrade Order+Position, Spot SpotTrade. Wallet permission пуст — sub'ы не могут сами делать transfer (transfer только через main API в UI).
- Bypass для миграции: см. [[feedback-bybit-migration-bypass]] о том как override-ить CLAUDE.md правила.
- Симлинк-трап: см. [[feedback-bybit-env-symlink]].
