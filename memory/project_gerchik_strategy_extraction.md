---
name: project_gerchik_strategy_extraction
description: Извлечение торговой стратегии А.М. Герчика из видеокурса LMS → playbook → детекторы для Pump&Dump бота (paper)
metadata: 
  node_type: memory
  type: project
  originSessionId: 4ea94e0a-63bf-4959-a4c4-d14ab5ec3fc8
---

Цель: чтобы AI-агент Pump&Dump торговал по методу А.М. Герчика. Источник — видеокурс
«Трейдинг Основы» в `lms.gerchik.com` (доступ Артёма; creds он даёт в чате, в память НЕ пишу).
Режим бота на старте (выбор Артёма 2026-06-10): **бот торгует сам, но paper**, пока копим статистику.

**Пайплайн извлечения (доказан end-to-end 2026-06-10):**
- Видео под DRM **VdoCipher/Widevine** — скачать нельзя. Берём через **рендер авторизованной
  сессии**: Playwright(chromium-1217, есть WidevineCdm) под Xvfb + pulse null-sink → ffmpeg x11grab.
  Риг Linux-only (на VPS). Скрипты в `/root/gerchik_recon/` (capture_one.sh, play_lesson_speed.js).
- Транскрипция: **faster-whisper large-v3 на GPU** (88с на 12-мин урок). 1x→эталон, **2x=безопасный
  максимум** (~98%, термины целы), 3x теряет точность — default 2x.
- Vision: кадры кропаются по плееру (888x500@284,140), читаются мной (графики уровней/слайды).
- Текст-бонус: 26 PDF-материалов курса (без DRM) + транскрипты.

**Инфраструктура (3 машины, каждая по делу):**
- VPS (Linux) = запись, 2 параллельных потока × 2x (4 ядра, load ~2.2 — есть запас).
- PC1 `tkach@100.99.211.123` (DESKTOP-F836B96, RTX 3090) + PC2 `borys@100.73.22.1` (host «Art», RTX 3090)
  = GPU Whisper (round-robin) + архив. Обе Windows, SSH без пароля (id_ed25519). faster-whisper стоит на обеих.
  См. [[project_trader_model_10]] — те же PC1/PC2 что в GA fan-out.

**Worklist:** 82 видео-урока в 15 блоках (`/root/gerchik_course/queue.txt`), videoId у всех.
LMS API: `GET /course/{id}` (blocks, Bearer), `GET /block/{id}?fieldMask=` (lessons),
`GET /lesson/{id}?fieldMask=video,additionalMaterials`. Плеер-URL: `/course/{cid}/block/{bid}/lesson/{lid}`.

**Артефакт (playbook):** `/root/gerchik_memory/` — `00_method_overview.md` (модель «стэк
преимуществ»: 50/50 + по +10% за уровень/предпосылки/короткий стоп), `levels.md` (уровни=провалы
горизонтального объёма, крупняк внутри канала, лимитник в DOM, горизонталь не зона, ≥4-6R) → 6 детекторов.

## АГЕНТ ПОСТРОЕН (2026-06-10) — ветка `feature/gerchik-core` в `/root/PumpDumpAI_Agent`
Пакет **`src/gerchik/`** (90 тестов зелёные), всё закоммичено, **запушено в origin**:
- `level_detector/pattern_detector/atr/trend_filter/setup_grade` — портированы из gerchik-trading-agent.
- `volume_levels.py` — объёмные уровни (провалы профиля), паранормальный бар, spacing ≥4R, held-level (Урок 1).
- `dom.py` — подтверждение уровня крупным лимитником (перцентиль).
- `pipeline.py` — детекторы→карточка(PreThesis, edge-score «стэк преимуществ»)→судья→Take/Skip.
- `journal_schema.py` — тезис ДО (PreThesis) + разбор ПОСЛЕ (PostAnalysis), ts_open/ts_close.
- `runner.py` — пайплайн→журнал; `api.py` — levels_payload + recent_theses.
- `chart.py` — рендер свечей+уровней (Pillow); `vision_judge.py` — Claude-судья.
- `claude_auth.py` — **Claude через OAuth подписки** (`~/.claude/.credentials.json`, как тутор-боты/@DexClaud; auth_token + beta oauth-2025-04-20). Сейчас бывает 429 (подписка общая) → fail-safe SKIP.
- `paper_engine.py` — paper-сделки (TAKE→позиция→тики→TP/SL→журнал, fee-aware-lite).
- `scanner.py` — живой цикл (BybitMarket: klines D/4H/1H+стакан+тикер).
- `web.py` — мини-панель (/, /chart.png, /api/thesis, /api/state, /api/analytics, /levels).
- `analytics.py` — день/неделя/месяц + разрезы (тип уровня/grade/сторона/символ), WR money-based.

**Прод-запуск:** systemd `gerchik-paper.service` (enabled, Restart=always) → `run_gerchik.py`
(config `config/gerchik.json`: 20 монет, paper-журнал `data/gerchik_paper.jsonl`, UI :8095, use_vision).
Лог: `journalctl -u gerchik-paper`. Перезапуск после правок кода: `systemctl restart gerchik-paper`.

**Доступ к панели (вне git, бэкапы сделаны!):**
- `http://187.77.148.44:8080/pumpdump.html` — торговая панель + **оверлей уровней Герчика** (кнопка «Γ уровни»); файл `/var/www/dashboard/pumpdump.html` (бэкап `.bak-*`).
- `http://187.77.148.44:8080/gerchik/` — панель агента (график/уровни/лента до-после/аналитика), за basic-auth дашборда.
- nginx: `/etc/nginx/sites-available/dashboard` — `location ^~ /gerchik/` → `127.0.0.1:8095`. ⚠ `^~` ОБЯЗАТЕЛЕН: без него regex-локация `\.(png|js|css)$` перехватывала `/gerchik/chart.png` → 404 (график не грузился); см. [[feedback_nginx_uploads_regex_trap]]. Также `add_header Cache-Control no-store`.
- ⚠ если деплой pumpdump.html из `/root/Space_Live/public/` — продублировать оверлей туда.

**Запись курса:** оркестратор жив (на 2026-06-11 **56/82 транскриптов**, все непустые; STT теперь и на PC2; 2 потока пишут параллельно). Новые правила из 56 → `gerchik_memory/course_findings_56.md`. **Вшито (commit e7c47a0):** ликвидность `MIN_TURNOVER_USD $5M→$50M` [b95db6ef], стоп пробоя `0.15 ATR` vs отбоя `0.10` [93b2c6fa]. Люфт вшит (commit b450489): `LUFT_FRAC_OF_STOP=0.20`, вход=уровень∓люфт (недобивание), риск=stop_size, цель/RR от входа. WR-гейт сделан (commit aee0a31): `promotion.py` min_trades=30/WR≥0.60, блокирует ⬆real (409) пока нет выборки, обход force:true; панель 🔒+tooltip. **Раскладка ТФ (commit 2547ea4→9890ee8→f664453):** 1D=уровни, 1H+4H=подтверждение (`htf_aligned`=тренд 1H И 4H), 5m=ТВХ-вход (`TF_LTF='5'`, `try_otboi` триггерит разворот на `klines_ltf`=5m, иначе фолбэк 1H). Подтверждено курсом «главное дневка и пятиминутка, дополнительно часовик» [a8dd2f3f]. ⏳ Кандидаты: 30м-БПУ-подтверждение для пробоя/ЛП; авто-промоутер по WR-гейту (отложен — flap-баг [[project_session_2026_06_05_real_sl_promoter]]). Пробелы курса: % депозита/дневной лимит/число позиций/правило БУ — НЕ названы числом. Архив на PC1 `C:/gerchik_course`. STT только на PC1 (PC2 large-v3/CUDA нестабилен → пустые txt).

**КУРС ДОБИТ 82/82 + БАТЧ ПРАВИЛ (2026-06-11):** Все 82 урока записаны/транскрибированы. 2 PLAY-FAIL урока (757c3cc2, 59b89de9) добиты после фикса **x11grab `-draw_mouse 0`** в `gerchik_recon/capture_one.sh` (Xvfb без указателя → ffmpeg падал `Failed to query xcb pointer`, писал 4.6с-обрубок). Разобраны +34 ранее не майненных урока (6+1 агентов) → **`gerchik_memory/course_findings_80.md`**: **ВСЕ пробелы свода_56 ЗАКРЫТЫ** — % депозита 1% (старт фикс $5–10) [d4baffce][62429c74]; дневной лимит = 3 стопа подряд → стоп дня [264b3a02]; риск/сделку=риск_дня/3; **БУ-правило** (после 1:1 однонаправленно / после 3:1 если был ретест) [6489542e][503ef59e]; **тейк-лесенка** (33/33/33, 30/10/60→7R best, 60/20/10/10) [01251b30][b3b5c990]; размер выборки 100 сделок/пакет 30 [264b3a02][46b8e3ff]; min 2 касания уровня; ЛП после >100% ATR; гейт активности 60–70% сценариев. **CONTRA:** сессия 9:30–11:00 исключать по статистике [caea1783]; WR 60–70% не универсален (есть режим WR≈2%/RR250:1) [0478da60]. **Вшито (commit f2aa83e, main, 281 тест):** БУ@1R в `paper_engine.on_price` (стоп→entry при +1R, закрытие reason=BE; journal/analysis уже знали BE; PAPER-симуляция, REAL-amend отложен); `MIN_LEVEL_TOUCHES=2` (swing/horizontal); `LP_MIN_ATR_FRAC=1.0` (ЛП только после перелёта >100% ATR) + skip-code `lp_atr_insufficient`. **Отложено** (отдельной измеряемой правкой): контртренд-стоп×0.5 (ломал инвариант-тесты, меняет qty×2), тейк-лесенка (риск двойного счёта [[project_paper_double_count_resolved]]), дневной лимит 3 стопа (REAL-only). roadmap обновлён до v0.2 (commit 4aca04d). ⚠ Артём снял «одна правка за раз» на ВРЕМЯ этой сессии пакетного обучения (правило остаётся для REAL-перехода).

**ПОРОГИ СВЕРЕНЫ С КУРСОМ (2026-06-10, commit 64d5207):** из 30 транскриптов извлечены числа с цитатами → playbook `gerchik_memory/risk_and_atr.md` + `entries.md`. Правки в коде: стоп `0.2→0.10 ATR_5D` (курс: 10% стандарт [458160db]); вес short_stop `0.15→0.10` (курс: +10%/фактор, НЕ макс [a7624bac]); ATR=High−Low за 5D без паранормальных [4349f879]; паранормал >2×ATR (уже верно), ≥3 касания (уже верно). **МИФЫ (НЕТ в курсе, не хардкодить как «Герчик»):** RR 3R/4R/6R (это house-инвариант проекта, не курс — цель=следующий уровень), множители 0.1/0.2×ATR, ≥5 касаний, Efficiency Ratio, % депозита. Не вшито пока: фильтр 75% ATR (только разворот при перерасходе) — кандидат следующей правки.

**ЭНЕРГИЯ ВШИТА (commit dbf474c):** фильтр 75% ATR (`pipeline.atr_exhaustion` + гейт в `build_setup`: вход в сторону уже исчерпанного ≥75% дневного ATR хода = чейзинг → отклоняется; фейд уровня/разворот разрешён) [4349f879]. Ширина канала (`channel_width_atr`, узкий≤3 / широкий≥5 ATR) → `PreThesis.regime` + **заведена в скоринг** (commit d0b8a1e): флаг `wide_channel`>5 ATR = +10% edge (растянутый долгий ход); узкий бонуса не даёт [21f5227b]. 94 теста зелёные.

**PAPER-СДЕЛКИ РАЗБЛОКИРОВАНЫ (commit 9344b0a):** Vision-судья стоял на 429 (общая OAuth-подписка) → fail-safe SKIP → 0 сделок. Теперь при ошибке Claude судья падает на **rule-решение** (TAKE если edge≥0.6 и RR≥min, иначе SKIP, пометка `[rule-fallback]`); `rule_fallback`/`fallback_edge_min` конфигурируемы (default on). После рестарта ЛП-трейдер сразу взял paper-сделки (BTCUSDT/XRPUSDT), журналы `data/gerchik_{otboi,proboi,lp}.jsonl` пишутся. **Персист позиций (commit 9590e3d):** PaperPosition сохраняется в `gerchik_<strat>_pos.json` на open/close и реадоптится при старте (`PreThesis.from_dict`) → рестарт НЕ переоткрывает сетапы (раньше плодил дубли trade_open-сирот). Дедуп существующих журналов: схлопывание trade_open без close (оставить последний на символ). Панель no-cache: meta+nginx+backend заголовки + штамп «v3». Панель (commit 7b70e3e): `/api/state` агрегирует позиции всех 3 движков + `/api/thesis` мёржит 3 журнала, обе с пометкой стратегии; в ленте колонка «стратегия», в позициях [Стратегия]. Регресс-тест `test_panel_js_syntax_valid` (node --check) ловит JS-баги панели.

**3 СТРАТЕГИИ-ТРЕЙДЕРА (commit 26370d7)** — ключевая архитектура по А.М. Герчику [b8e4d596 «три к одному»], статистика по трём отдельно [c0560563]. `strategies.py`: `try_otboi` (фейд непробитого уровня + 1H разворот), `try_proboi` (дневное закрытие ЗА уровень → продолжение, без чейзинг-гейта, флаг atr_room), `try_lozhny_proboi` (прокол хвостом + возврат внутрь → фейд, стоп за хвост). `build_setup(strategy=)` + `STRATEGY_FLAGS` маскируют предпосылки per-strategy (пробой=ближний ретест+поджатие+atr_room; отбой/ЛП=дальний ретест+длинный хвост). Демон поднимает 3 движка с журналами `data/gerchik_{otboi,proboi,lp}.jsonl`, сканер кормит все за один фетч. Панель `/api/traders` + сравнение WR/PF/net (вид из 4Bots, стратегии из курса). Цель: что прибыльнее на дистанции. Playbook: `gerchik_memory/strategies.md`. ⚠ default `build_setup` strategy=отбой (обратная совместимость).

**РУЧНОЙ ПЕРЕВОД paper↔real (commit c96c55f):** `trader_mode.py` — режим per-стратегия в `data/gerchik_traders_mode.json` (default ВСЁ paper). `GerchikPaperEngine(mode, executor, leverage=20)`: при REAL `on_signal` судит ОДИН раз → real-вход (`Executor.place_entry` + `set_sl_tp` с SL-retry) → журнал mode=REAL; вход/SL fail → НЕ открываем (без сироты); REAL close флэтчит остаток. `runner.journal_open` (журнал после TAKE). Панель: чип режима + кнопка ⬆real/⬇paper; `POST /api/trader_mode` (REAL требует `confirm:'REAL'` + наличие executor). run_gerchik строит общий REAL `Executor` + `_load_env_file` форсит BYBIT_* (защита от [[feedback_sl_zero_position_race]] test_key_123). risk_usd=1.0 ($1/сделка), exits exchange-managed, realized в журнале ≈ по SL/TP-уровню (не closed-pnl API). 248 тестов.

**ОТБОР ИНСТРУМЕНТОВ ВШИТ (commit a326e2e):** `selection.py` — относительная сила (BTC=прокси индекса, `is_stronger_than_market`: LONG сильнее/SHORT слабее рынка) оживила мёртвый флаг `stronger_than_market` (был всегда False) [a7624bac]; прокинуто `build_setup(klines_market=)→evaluate→on_signal→scanner`. Скрининг вселенной: отсев по энергии (ATR≥1.5%) и ликвидности (оборот≥$5M), scanner тянет BTC D-свечи раз за проход. Детали отбора («чистый график») — в незаписанных уроках (playbook `selection.md` помечен TODO). 101 тест зелёный.

**ДОП. ТИПЫ УРОВНЕЙ (commit db62fc2):** `levels_extra.py` — **зеркальный** (`mirror_levels`: цена была И swing-high, И swing-low = сопротивление↔поддержка, strong) ВШИТ в `_candidate_levels` (ценен для 24/7) [556f8f02]; **гэп** (`gap_levels`: истинный разрыв без перекрытия диапазонов = closе пред.дня + точка открытия) и **IPO** (`ipo_levels`) готовы+протестированы, но в крипто-пайплайн НЕ подмешаны (Артём: гэпов на крипте нет; IPO нужна полная история) — включаются добавлением в `_candidate_levels`. 106 тестов.

**ТОЧКА ИЗЛОМА ТРЕНДА / БСУ (commit 8c37781):** `trend_break_levels` — «первый тип уровня» курса: одиночный разворот резкого хода (≥2×ATR в пивот = упёрся в лимитного игрока), отличается от horizontal (многократный излом, ≥3 касания) тем что touches=1 [556f8f02]. ВШИТ в `_candidate_levels`. **ИНВЕНТАРЬ: все 9 типов уровней курса покрыты** (таблица в `gerchik_memory/entries.md`): активны 6 детекторов уровней (horizontal=многократный, volume, paranormal_bar, mirror, trend_break, **consolidation=проторговка VWAP зоны накопления** commit 3d7b4a6 [eb0ebce1]) + DOM-усиление (лимитный игрок); gap/ipo готовы но off (нет на крипте / нужна история). NB: «узкая проторговка вдоль уровня» = **поджатие** — отдельная предпосылка (НЕ тип уровня). **ВШИТО — 2 вида поджатия (commit 0559259, 80fef69):** (1) `is_squeeze` = направленный подход на маленьких барах (диапазон ≤0.5×ATR + closes ±1% от уровня) → флаг `squeeze` +10%; (2) `is_tight_zone_along_level` = ФЛЭТ узкая проторговка вдоль уровня (band ≤1×ATR + дрейф ≤0.5×ATR + уровень внутри зоны, нет направленного хода) → флаг `tight_zone` +10% [eb0ebce1]. Курс различает их явно. **Свободная зона (commit 207acd9):** `pipeline.has_free_zone` — путь вход→цель не «заражён» встречными сильными/средними уровнями → флаг `free_zone` +10% [03c021c7]. **Ближний ретест (commit 3d1c4bf):** `pattern_detector.is_near_retest` — свежий контакт + мелкий откат (closes ≤1×ATR от уровня) = быстрый возврат vs дальний подход → флаг `near_retest` +10% [eee2e992]. Edge-стэк теперь 12 факторов (база 0.5, cap 0.95). 120 тестов. Предпосылки готовы: short_stop, stronger_than_market, room_to_move, htf_aligned, dom_confirmed, wide_channel, squeeze, tight_zone, free_zone, near_retest, strong_level, preconditions(vol/pin). ⚠ ВАЖНО (Артём): числа из курса вроде «проторговка 90-100 → средняя 95» — это ПРИМЕРЫ для иллюстрации, НЕ зашивать в формулы; consolidation использует общий VWAP зоны (правильно), не хардкод. 113 тестов.

**ЗАПАС ХОДА ВШИТ (commit 952a540, main, 283 теста):** `ROOM_MIN_ATR_FRAC=0.40` в `build_setup` — вход В СТОРОНУ дневного хода (moving_with) требует остаток ATR ≥40%, иначе reject `no_atr_room`; ловит исчерпанные ПРОБОИ, которые чейзинг-гейт (0.75, только фейды) пропускал [b3b5c990]. +2 теста (исчерпанный пробой reject / ранний пробой ок).

**TODO (resume):** курс 82/82 готов, свод_80 полон. Следующее из очереди (roadmap §9): техстоп ≤расчётный+30%→режем позу; контртренд-стоп×0.5 (с замером); тейк-лесенка (осторожно с partial-close учётом); дневной лимит 3 стопа (REAL-only); затем LLM-рефлектор (недельный разбор) → накопить paper-статистику до real ([[feedback_one_tweak_at_a_time]] снова в силе для REAL, [[project_real_trades_baseline]]).
Копирайт курса — приватно. Привязка: [[project_pumpdump_selftuning]], roadmap: `PumpDumpAI_Agent/docs/GERCHIK_AGENT_ROADMAP.md` + `CLAUDE.md`.
