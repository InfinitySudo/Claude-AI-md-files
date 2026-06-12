---
name: project_gerchik_chart_levels
description: "Уровни Герчика на панели агента — единый источник chart_levels(), held-фильтр только для отбоя"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5953d251-e235-4db9-839e-85e0af7d45ee
---

Gerchik-агент (`/root/PumpDumpAI_Agent`, `src/gerchik/`). Артём: главное — агент должен строить уровни ПРАВИЛЬНО по методу Герчика (верный уровень → импульс → профит; неверный → SL).

**Корень бага (2026-06-12, commit 917c0d0):** торговый пайплайн строил полный набор исторических уровней (`_candidate_levels`: horizontal/volume-впадины/paranormal/**trend_break=БСУ — «первый уровень курса»**/mirror/consolidation, выше И ниже цены), но ПАНЕЛЬ `/gerchik/` рисовала урезанный набор (только detect_levels+volume+paranormal) → не было поддержек ниже цены.

**Решение:** `pipeline.chart_levels(klines)` — ЕДИНЫЙ источник «уровни как видит агент» для графика: дедуп близких (`CLUSTER_DEDUP_PCT`) + §6 дистанция ≥~4×стоп (`0.4×ATR`, не частокол) + баланс сторон (отдельный кап выше/ниже цены, иначе плотная лестница trend_break вытесняет поддержки снизу). web.py `_chart_levels` зовёт его.

**Важные нюансы (faithfulness к курсу `/root/gerchik_memory/levels.md`):**
- held-фильтр `level_not_pierced` (§5 «пробит телом») применяется ТОЛЬКО в отбое (`strategies.try_otboi:45`) — НЕ глобально: пробой/ЛП легитимно работают с пробитыми уровнями. Глобальный held по 200 барам убивал ВСЕ исторические уровни (цена ходила далеко).
- `Level.type` (поле) + подписи на графике: гор/об/пб/излом/зерк/кон — видно ОТКУДА уровень.
- klines теперь несут `ts` (для маркеров баров входа/выхода).

**Готово (2026-06-12):** маркеры сделок + попап (PNG /api/chart, commit 8d4fd1d), скриншоты входа/выхода для AI (`scanner._save_trade_shot` → data/screenshots/<стратегия>/, gitignore), и **фаза 2 — живой интерактивный график** (commit bd973e0): `/api/livechart` + TradingView lightweight-charts@4.1.3 (CDN) в панели /gerchik/ — свечи+объём+зум, уровни линиями с подписью типа, E/SL/TP/BE позиции, маркеры ▲/▼/✕/○ на правильных внутридневных барах, селектор ТФ (5m/15m/1h/4h/D), toggle уровней, клик→попап. Проверено headless Chromium (0 ошибок). Свой self-contained график в git (НЕ трогали pumpdump.html /var/www). См. [[project_gerchik_strategy_extraction]], [[project_gerchik_proboi_subtypes]].
