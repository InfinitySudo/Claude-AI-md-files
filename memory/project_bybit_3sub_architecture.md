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

Старые отжившие аккаунты:
- uid 539929753 раньше был общим для TradingBot+AI-agent (один кошелёк, конфликт margin) — теперь чисто AI-agent через отдельный sub3 ключ.
- uid 100548867 — старый Gerchik sub, больше не используется (баланс перенести руками в UI и удалить старые API ключи Htba1U/NVFHin).

**Why:** До миграции TradingBot и AI-agent делили один кошелёк → risk_manager TradingBot'a видел позы AI-agent'a как orphan и пытался их сопровождать через dust-sweep. После — каждый бот изолирован, никакого cross-contamination.

**How to apply:**
- `/root/gerchik-trading-agent/src/env_config.py:bybit_creds()` читает `BYBIT_AI_AGENT_API_KEY` с fallback на `BYBIT_API_KEY` — не сломать этот fallback.
- IP whitelist на всех 3 ключах: `187.77.148.44`, `46.8.232.182` (Артём диктовал при создании).
- Все 3 sub имеют `unified: 0` (classic, не UTA). Linear USDT perp работает, но `accountType=CONTRACT` для wallet может быть нужен на отдельных эндпоинтах.
- Permissions на всех: ContractTrade Order+Position, Spot SpotTrade. Wallet permission пуст — sub'ы не могут сами делать transfer (transfer только через main API в UI).
- Bypass для миграции: см. [[feedback-bybit-migration-bypass]] о том как override-ить CLAUDE.md правила.
- Симлинк-трап: см. [[feedback-bybit-env-symlink]].
