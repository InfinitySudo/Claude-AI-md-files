---
name: project_per_trader_entry_split
description: "Per-trader разделение входа (Фаза 1 = whitelist монет готов) + аналитика RR/MFE: длинный хвост = режим рынка, не символ; адаптивный R не бьёт R≈1"
metadata:
  node_type: memory
  type: project
  originSessionId: ce36190d-1e66-4ff8-83ca-991871de4019
---

4BotsBybit-Trading. Трейдеры A–F раньше входили по ОДНОМУ глобальному сигналу (signal bot → fan-out `main_bot_v3.py:1471` всем одинаково); различались только движком выхода. Цель — развести вход per-trader. План в 3 фазы (см. [[project-trader-model-10]]).

**✅ Фаза 1 готова (commit `646690a`, 2026-06-05):** per-trader **whitelist монет**.
- Хранение: `strategy_parameters.<cfg>.symbol_whitelist` (список) в `trading_v3_artem.json`. **Пусто/нет = все символы** (backward-compat).
- `main_bot._trader_symbol_whitelist(strategy)` (читает self.config, освежается рестартом) + фильтр в fan-out перед `process_signal` (skip если symbol не в whitelist).
- API: `GET/POST /api/v2/traders/<id>/symbols` (валидирует ⊆ `_ga_active_symbols()`=config/symbols.json, пишет json, рестартит tradingbot; пустой список стирает ключ). `/api/v2/traders` отдаёт `symbol_whitelist`/`symbol_count`.
- UI (`/var/www/dashboard/v2.html`, unversioned — бэкап делал): кнопка «🪙 Монеты: N/все» в карточке → модалка-пикер (поиск/все/снять). 308 pytest passed.
- ⚠ **UX-инвариант (требование Артёма):** Signal Criteria (volume/spike/BS/EMA/BTC-regime) в Фазе 1 ФИЗИЧЕСКИ ГЛОБАЛЬНЫ — НЕ выносить в карточки; помечены «🌐 глобальные» в `#sec-signal` sub и read-only строкой в карточке, чтобы не было иллюзии изоляции.

**✅ Фаза 2 готова (commit `3e8e75e`, 2026-06-05):** per-trader **пороги входа** volume/spike/B-S.
- Хранение: `strategy_parameters.<cfg>.entry_filter = {min_volume_usd, min_spike_ratio, min_bs_ratio}` (любой ключ опционален; нет = без ограничения).
- ⚠ Плумбинг-фикс: `_get_next_signal_from_db` SELECT РАНЬШЕ не тянул метрики — дописал `volume_usd, spike_ratio, buy_percent, sell_percent` (в КОНЕЦ SELECT, чтобы не сдвинуть row[7..11]) → теперь в `signal_data`.
- `_eval_entry_filter` (pure, staticmethod) + `_trader_entry_filter` (читает self.config) → фильтр в fan-out после whitelist. None-метрика = пропуск (не блок). `bs_ratio = max(buy_pct,sell_pct)/min(...)` (mirror глобального «dominant > N×other»).
- API: `POST /api/v2/traders/<id>/entry-filter` (валидация vol≥0/spike≥1/bs≥1, null/пусто чистит, рестарт). `/api/v2/traders` отдаёт `entry_filter`. UI: блок «Фильтр входа (≥ global)» с 3 инпутами, плейсхолдер=глобальный пол из SETTINGS. 315 pytest.
- ⚠ Инвариант: per-trader только УЖЕСТОЧАЕТ; ниже global без эффекта (signal bot уже отфильтровал). signal_strength НЕ добавляли (анализ: STRONG хуже).

**✅ Фаза 3 готова (commit `321d526`, 2026-06-05):** per-trader **EMA-gate + BTC-regime**.
- ⚠ Сделано ПРОЩЕ, чем планировалось: **целиком в main_bot, БЕЗ правок signal bot, БЕЗ миграции signals_queue, БЕЗ payload**. (BTC-regime уже был в main_bot на fan-out 1211; EMA по REST main_bot тоже умеет.)
- Рефактор: `_btc_would_block_long` (считает независимо от глобального enabled) выделен из `_btc_regime_blocks_long` (глобальный master на 1211 не тронут). Новый `_symbol_ema_would_block` (per-symbol EMA по REST+кэш, tf/period из `signal_bot_config.json` ema_gate) + pure `_ema_blocks(dir,price,ema)`. `_trader_regime_block` чтит `entry_filter.require_ema_gate`/`require_btc_regime`; фильтр в fan-out после Phase-2. Всё fail-open.
- Хранение: те же `strategy_parameters.<cfg>.entry_filter` (були). Endpoint `/entry-filter` принимает 2 буля. UI: 2 чекбокса в блоке «Фильтр входа». 321 pytest (поправил `test_btc_regime` stub под делегат).
- Инвариант: глобальный гейт = master (когда ON режет всех); per-trader = опциональное включение для себя когда глобально OFF. EMA tf/period — глобальные.

**🎉 Разделение входа A–F ПОЛНОЕ:** монеты (Ф1) + пороги vol/spike/BS (Ф2) + EMA/BTC гейты (Ф3) — всё per-trader через `strategy_parameters.<cfg>.{symbol_whitelist, entry_filter}` + fan-out фильтры в `main_bot_v3.py:~1471`.

**✅ 2026-06-05 эксперимент «широта вселенной» настроен:**
- Корзины (по 24h-обороту ∩ active252): **A=BTC, B=top10, C=top50, D=top100, E=top200** (вложенные). Применены через Phase-1 symbols endpoint.
- **Движки A–E выровнены на `cons`** (commit `51546d7`, trader_registry): чтобы единственное различие = корзина. ⚠ suffix НЕ трогали ((t)/(a) зашиты в close_reason истории). trend/aggr движки стали dead-code (тест trend перепрофилирован).
- **✅ TP/BE-параметры A–E тоже выровнены под conservative** (2026-06-05, через 48× `/api/settings`, не код): все = R[2,2.25,2.5,2.75,3] dist[0.4,0.3,0.3,0,0] be_act2.0 be_off0.35. Теперь **эксперимент чистый: A–E различаются ТОЛЬКО корзиной символов** (engine cons + TP идентичны). config/trading_v3_artem.json — runtime state, не в git.
- **Per-trader Beacon** (commit `b26d6f4`): `/api/v2/beacon?source=Trader X` уже считал per-trader кривую; обобщил `/api/v2/beacon/apply` на `target=<id>` (пишет single-TP `tp_ratios=[R*]/dist=[1.0]` в блок трейдера, гард n≥min_trades, trader_0 запрещён). UI: A–F в `#beacon-source`, кнопка Apply таргетит выбранного. Авто-подстройка остаётся F-only. ⚠ Beacon по трейдеру отражает ИСТОРИЮ его сделок — после смены корзины данные сдвигаются к новому универсу не сразу (Trader A сейчас n=806 от старых all-symbol сделок).
- Рекомендация по адаптиву: **single-TP adaptive** (как F), multi-level не делаем (Beacon-математика = один 100%-TP). Узкие корзины (A,B) накопят n не сразу.

**✅ Beacon basket-aware + single-TP применён A–E (2026-06-05, commit `d95410f`):**
- `beacon.fetch/sweep` приняли `symbols=[...]` (`symbol = ANY`). Эндпоинты: `GET /api/v2/beacon?basket=<tid>` и `POST /beacon/apply {basket}` считают MFE по whitelist трейдера КРОСС-ТРЕЙДЕР (source=all) — правильная выборка под новую корзину сразу (а не по старым сделкам трейдера). UI: в `#beacon-source` опции «Trader X · корзина».
- Применил single-TP на 30d (n всех ≥50): **A=BTC R2.32, B=top10 R1.142, C=top50 R0.903, D=top100 R0.866, E=top200 R0.819** (tp_ratios=[R*], dist=[1.0], tp_count=1). Перезаписало выровненную 5-TP лесенку — это переход к adaptive single-TP per basket. ⚠ Окно 30d (с майским чопом) даёт R~0.8-0.9 для широких корзин; узкий BTC держит R2.32 (длинный хвост).
- ⚠ Авто-каданс остаётся F-only (basket-aware per-trader авто-подстройка — не делали). Значения статичны до ручного переприменения.

**✅ Per-trader basket-aware авто-каданс готов (2026-06-05, commit `c03fb93`):**
- `_maybe_recalibrate_beacon` обобщён с F-only на ЦИКЛ по `reg.all_traders()` с флагом `strategy_parameters.<cfg>.beacon_auto=true`: каждый раз в `recalibrate_hours` берёт sweep по СВОЕЙ корзине (symbol_whitelist, source=all), ставит single-TP `[R*]/[1.0]`, гард n≥min_trades + гистерезис min_ratio_delta, ОДИН atomic hot-write/цикл (без рестарта), TG-сводка.
- Окно: глобальное `trader_beacon.window_days=14` (BEACON_DEFAULTS) + per-trader override `beacon_window_days`. **A=BTC→30d** (узкая корзина не набирает n за 14d), B–F→14d.
- ⚠ Фикс латентного бага: `os.replace` в write-пути без `import os` (старый F-only путь почти всегда упирался в гистерезис до записи → не всплывало).
- API: `POST /api/v2/traders/<id>/beacon-auto {enabled,window_days}` (hot), setting `beacon_window_days`. UI: чекбокс «🔭 авто-TP (basket)» + поле окна в карточке; дефолт-окно в панели Beacon.
- **Включено A–F** (A окно 30d). Первый цикл: C 0.903→1.816, D 0.866→1.711, E 0.819→1.655 (14d-оптимумы выше 30d), A=2.32 (BTC/30d), B/F держит гистерезис. Мастер `trader_beacon.enabled` вкл.

Полный per-trader цикл замкнут: вход (корзина+пороги+гейты) + выход (basket-adaptive single-TP).

**✅ Per-trader GA (2026-06-05, commit `ad4a650`):** существующий GA-стек (`src/backtest.py` kline-replay + `scripts/ga_optimizer.py` VPS + `scripts/gpu/ga_optimizer_gpu.py` PC1, запуск через SSH+PowerShell, `_start_ga_on_*`, `pc1_status_poller.py`) теперь гоняется **по корзине трейдера**.
- `/api/ga/run {trader_id, target}` → symbols = корзина трейдера; target vps/pc1/**pc2**. `_start_ga_on_pc1`→`_start_ga_on_gpu(target)`: PC1 хардкод (100.99.211.123/tkach/ga_gpu), **PC2 из env** `GA_PC2_HOST/USER/DIR` (user дефолт «Artem Borysiuk»); пустой host → 400 «PC2 не настроен». ⚠ PC2 ещё нужен host(Tailscale)+ga_gpu+SSH-ключ.
- `/api/ga/apply-trader {trader_id, rank}` = **ENTRY-ONLY**: пишет GA-`spike/bs/volume` ранга в `entry_filter.min_*` трейдера, **TP НЕ трогает** (за выход — Beacon). Проверено: tp_ratios остался [1.816] после apply. `/api/v2/traders` отдаёт `ga_running/ga_target/ga_gen/ga_has_results`. UI: в карточке «🧬 GA вход» (машина/pop/gens/Run/Apply).
- ⚠ **MVP последовательный** (один ga_status, 1 прогон за раз). Параллель PC1+PC2 — follow-up (нужен per-run статус) когда PC2 пропровижен. **Комиссии/слиппедж в sim — TODO** (sim GROSS; gene-bounds spike≥4 + diversity-penalty частично гасят over-trade). PC1 live-прогон отсюда не гонял (код = генерализация рабочего pc1-пути).
- Разделение: **GA=вход, Beacon=выход** — не конфликтуют.

**✅ 2026-06-05 GA: PC1-фикс + комиссии + PC2-host (commit `87fa87a`):**
- ⚠ Регресс: моя generalization `_start_ga_on_gpu` СЛОМАЛА запуск PC1 (одинарные кавычки вокруг пути run_ga.ps1 → powershell печатал баннер, «Could not parse PID»). Фикс: кавычить путь ТОЛЬКО при пробеле (PC1 'tkach' без пробела — без кавычек, как работало; PC2 'Artem Borysiuk' — с пробелом → двойные).
- Комиссии: `src/backtest.py` (VPS) РАНЬШЕ был GROSS, хотя `ga_optimizer.py` комментировал «taker fee baked in» — латентная дыра. Добавил `ROUNDTRIP_FEE_PCT=0.11%` (env `GA_ROUNDTRIP_FEE_PCT`) в `simulate_trade` (SKIP не штрафуем). Слиппедж уже добавляется ОТДЕЛЬНО в фитнесе `ga_optimizer.py` (2×SLIPPAGE_PCT_PER_SIDE) — не дублируем. **GPU-sim (`gpu/ga_optimizer_gpu.py`) УЖЕ вычитает 2×0.10+0.011 funding** — не трогал. 2 теста обновлены на net.
- **PC2 = Tailscale «art» = `100.73.22.1`** (прошит дефолтом в `_gpu_machine('pc2')`). Хост ДОСТУПЕН (SSH коннектится), но **auth fails: `Permission denied (publickey)` для user «Artem Borysiuk»** → нужен верный SSH-логин + VPS-pubkey в authorized_keys PC2 + развёрнутый ga_gpu (провижн Артёма). Env override `GA_PC2_USER/HOST/DIR`.
- ⏸ **Параллель PC1+PC2 ОТЛОЖЕНА**: нужен рефактор удалённого `pc1_status_poller.py` (per-trader статус/результаты файлы) — тестировать только на живой 2-й машине; не делал, чтобы снова не сломать рабочий PC1 непротестированной remote-правкой. Сейчас GA последовательный (1 прогон).

**✅ 2026-06-05 GA ПЕРЕСОБРАН под single-TP (commit `b5a46c3`):**
- Все трейдеры cons single-TP → GA-гены ужаты с ~25 (cons 3-TP/trend 5-TP/aggr %) до **11**: spike/bs/volume, atr_multiplier, **tp1_ratio** (один TP), be_activation, be_offset, cooldown/atr_daily/volume_avg/trend bars. Быстрее/меньше оверфита.
- `ga_optimizer.py` (VPS) + `gpu/ga_optimizer_gpu.py` (PC1) переписаны ИДЕНТИЧНО (имена/порядок генов сверены равными); evaluate гоняет одну cons single-TP стратегию (убран combine 45/35/20). backtest-движок не трогали. VPS прогон валидирован end-to-end (выдал tp1_ratio).
- `/api/ga/apply-trader {mode}`: **full** = entry_filter + tp_ratios=[tp1_ratio] + BE (GA-доли ×100 → %) + ВЫКЛ beacon_auto; **entry** = только вход. `/api/ga/trader-result` = GA rank1 + test-метрики + **Beacon(MFE) R* по корзине** (сравнение GA-TP↔MFE). UI: GA-панель в карточке (параметры + строка GA vs Beacon, подсветка Δ) + кнопки «вход+TP»/«только вход»; цели прогона только PC1/PC2 (VPS убран). 321 pytest.
- ⚠ **PC1/PC2 крутят СВОЮ локальную копию `ga_gpu`** — авто-синка с VPS-коммита НЕТ (`_start_ga_on_gpu` шлёт run_ga.ps1 напрямую; `launch_ga_synced.sh`/run_ga.ps1 git pull не делают). **Чтобы новые single-TP гены заработали на PC1 — нужно обновить ga_gpu копию на PC1 (git pull там).** Иначе прогон выдаст старый формат. Артём валидирует на PC1 после обновления.
- ⚠ Beacon vs GA на TP: оба пишут tp_ratios — поэтому full-apply ВЫКЛючает beacon_auto трейдера. «только вход» оставляет выход за Beacon.

**✅ 2026-06-05 GA-цепочка добита до чистых результатов (commits `586e089`→`9671e67`):**
- **Single-symbol guard:** GPU-движок абортил `<5 symbols` → Trader A (BTC=1) не считался; стало `<1` (commit 547ddfd).
- **Свежее окно:** `api_ga_run` шлёт `-Start/-End` (последние ~90д, `ga_days` в payload) в run_ga.ps1 (раньше брал хардкод Feb–May) (7de4f05).
- **Поллер freshness:** `_finalize` проверяет, что remote `ga_gpu_results.json` mtime > started_at; иначе `failed` (раньше аборт показывался как «completed» со стейл-файлом) (7de4f05).
- **BE-эксплойт убит:** GA находил `be_offset>be_activation` → симулятор фиксировал выход на недостигнутом уровне = фейк-профит (WR67/Sharpe17). Клампим offset≤activation в `backtest.py` + GPU `simulate_trade_kernel.py pack_spec` + clamp генов (vps+gpu) (9671e67). После фикса BTC честно показал net−0.58/⚠overfit/22 сделки.
- **Trader F демоут починен (`f03271b`):** mode-endpoint `/api/v2/traders/<id>/mode` теперь штампует `trader_promoted_at` при REAL (раньше нет → промоутер судил всю 7д-историю → демоутил). F переведён в real, держится.
- **Вывод по GA:** на 1 монете (BTC) GA = overfit (22 сделки = размер выборки, не данных; баров-то 25k). GA осмыслен на ШИРОКИХ корзинах (C/D/E top50-200 = сотни-тысячи сделок). Для узких — Beacon (MFE) надёжнее.

**⚠ КРИТИЧНО — деплой на PC1 (ops-знание):**
- PC1 = `tkach@100.99.211.123` (Tailscale `desktop-f836b96`), dir `C:/Users/tkach/ga_gpu` — **ПЛОСКАЯ копия `scripts/gpu/`, НЕ git** (нет .git). Деплой = `scp scripts/gpu/<file> tkach@PC1:ga_gpu/`. Пути в ssh: относительные (`ga_gpu/...`) работают, абсолютные `C:/...` иногда «path not found».
- **После scp ОБЯЗАТЕЛЬНО чистить `__pycache__`** (scp не двигает mtime → Python грузит стейловый .pyc → крутит старый код; на это ушло 3 ложных «ничего не поменялось»). `run_ga.ps1` теперь чистит сам, но при ручном scp — `ssh PC1 'rmdir /s /q ga_gpu\__pycache__'`.
- run_ga.ps1 запускает `pc1_run_wrapper.py` → `import ga_optimizer_gpu`. Окно/symbols/pop/gens через args.
- Поллер (`pc1_status_poller.py`) крутится на VPS (systemd-run), не на PC1.
- **PC2 = `100.73.22.1` (Tailscale `art`), user «Artem Borysiuk»** — host ДОСТУПЕН, но SSH `Permission denied (publickey)`: нужен VPS-pubkey в authorized_keys PC2 + развёрнутый ga_gpu (провижн Артёма). env `GA_PC2_HOST/USER/DIR`.
- Прогоны GA пока **последовательные** (1 ga_status); параллель PC1+PC2 ждёт провижена PC2 + per-run рефактор поллера.

**Аналитика RR/MFE (методология Beacon, fee 0.11%, SL≈1.5%), ключевые НЕочевидные выводы:**
1. **Высокий RR — ловушка.** На наших данных hit падает быстрее роста RR: 1:3 нужен WR~27%, факт ~15% → E≈−0.70; 1:5 надо ~18%, факт ~7%. Оптимум E ≈ R1.0 (TP~1.5%). Причина: короткий хвост MFE.
2. **STRONG/WEAK инвертирован:** WEAK прибыльнее STRONG (E* +0.15 vs +0.02) — «STRONG» (spike>4+перекос) = выдыхающиеся импульсы. Не использовать strength как ось для RR.
3. **Длинный хвост = РЕЖИМ РЫНКА, не символ.** Помесячно: в мае корзина ADA/XPL/BNB/BTC/DOGE/TRX короткохвостая и минусовая (E@R3 −0.7), в июне (тренд) — R*4.6, E@R3 +1.0. Недельно R* монотонно рос. Статический high-RR whitelist опасен (кровил бы в мае). Только BTC/BNB держат R*≥2 даже в майском чопе — слабые кандидаты на структурный хвост.
4. **Адаптивный R (Beacon-rule) НЕ бьёт фикс R≈1** на walk-forward: adapt −0.08, fixed R1 −0.05, R3 −0.68, oracle +0.11. На агрегате всех символов оптимум стабильно ~1, длинный хвост разбавлен → Beacon на «all» его не ловит. Вывод: держать R≈1 базой; символьный edge (BTC/BNB) тестировать отдельно форвардом, не доверять авто-Beacon его найти.

Связано: [[project-trader-model-10]], [[project-session-2026-06-05-real-sl-promoter]].
