---
name: project-dashboard-be-sl-tabs
description: "2026-05-21 — добавлены 2 новых toptab в v2 dashboard: BE A/B/C comparison + SL-analysis + rule-based BE recommendation engine. /api/v2/be-compare, /api/v2/be-recommend, /api/v2/be-apply, /api/v2/sl-analysis. UI копия MFE-tab паттерна."
metadata: 
  node_type: memory
  type: project
  originSessionId: 8d8a9d06-61d1-431c-bd4f-b7be01653cbd
---

С 2026-05-21 в `/v2.html` появились две новые вкладки между MFE и GA:

**⚖️ BE** — таблица per-strategy с main row (текущая BE-конфига) и shadow row (no-BE контроль, `is_shadow=true` paper-only). Колонки: N, WR, PF, Net, BE-close%, TP1-close%, TP-any%, SL-close%, peak-after-BE%. ★-маркер на «победителе» каждой метрики между main и shadow. Под таблицей блок Recommendation с 3 правилами + кнопкой Apply (confirm phrase `APPLY BE`).

**🛡 SL** — per-strategy MAE-распределение (p50, p90), adverse-R (MAE/SL-distance), SL-before-TP1% (флаг «SL слишком тугой»). Top 15 SL-magnet symbols (≥3 trades, ≥2 SL, ORDER BY sl%/net) — кандидаты для blacklist. Recommendation блок: tighten (adv-R<0.5) / loose (sl_before_tp1>50%).

**Endpoints (additive, не ломают existing):**
- `GET  /api/v2/be-compare?source=paper|real&days=&baseline=`
- `GET  /api/v2/be-recommend?source=&days=&baseline=`  (rule-based, no ML)
- `POST /api/v2/be-apply` (body: confirm_phrase, strategy, be_activation_pct, be_price_offset_pct)
- `GET  /api/v2/sl-analysis?source=&strategy=ALL|...&days=&baseline=`

**Why:**
- Нужно сравнить параллельный A/B/C эксперимент [[project-be-per-strategy-experiment]] и shadow=no-BE контроль [[project-tp-shadow-ladder]] глазами, не CLI.
- Recommendations показывают наиболее прибыльные настройки на текущих данных (но Apply нельзя жать минимум 30 дней — нарушит эксперимент).
- SL-анализ нужен для tightening/loosening и blacklist кандидатов.

**How to apply:**
- При добавлении новой стратегии (например GERCHIK) — расширить `_BE_STRATEGY_LAYOUT` в `src/dashboard_api_v3.py` (рядом с `_MFE_STRATEGY_LAYOUT`).
- Apply BE триггерит restart bybit-tradingbot. До 2026-06-21 жать не нужно [[project-be-per-strategy-experiment]].
- Shadow row для real source всегда пуст (real не имеет контрольной группы).
- Tab toggle для tightening SL на основе adverse-R: requires n≥30 per strategy.

**Файлы:**
- `src/dashboard_api_v3.py` — endpoints начиная с `_BE_STRATEGY_LAYOUT` ~line 4825 (после `/api/mfe/apply`).
- `index_v2.html` — tabs `data-toptab="be"` и `data-toptab="sl"` (~line 503); JS `loadBE()`, `loadSL()` рядом с `loadMFE()` (~line 3260).
- Deploy: `cp index_v2.html /var/www/dashboard/{v2.html,index.html}`.

**Verification:**
```bash
curl http://127.0.0.1:8000/api/v2/be-compare?source=paper&days=30 | jq .
curl http://127.0.0.1:8000/api/v2/be-recommend?source=paper&days=30 | jq .
curl http://127.0.0.1:8000/api/v2/sl-analysis?source=paper&days=30 | jq .
```

**Outside scope:**
- ML recommendation engine — до 300+ real trades [[project-real-trades-baseline]].
- Auto-apply через cron — нет; только ручная кнопка.
- Изменение auto_tp_tuner.py — отдельная задача.

**⚠ Caveat про recommend-engine и эпохи настроек:**
До 2026-06-21 рекомендации `/api/v2/be-recommend` опираются преимущественно на данные **старых** BE-настроек (CONS 0.5/0.15, TREND 0.8/0.5, AGGR 1.5/0.5), а не новых (CONS 1.6/0.6, TREND 1.8/0.8, AGGR 1.5/0.5 — стартовали 2026-05-21 19:00 UTC, см. [[project-be-per-strategy-experiment]]). Никаких «recommendation для текущего эксперимента» в первые 30 дней не существует — это статистика старой эпохи. Apply кнопка должна оставаться нетронутой до накопления ≥50 closed trades per strategy с `entry_time >= 2026-05-21 19:00 UTC`.

**С 2026-05-21 ~20:00 UTC `since=` фильтр доступен** в 4 endpoint'ах: `/api/v2/be-compare`, `/api/v2/be-recommend`, `/api/v2/sl-analysis`, `/api/mfe/calibration`. Clamps SQL к `entry_time >= since` — игнорирует baseline+days. UI: dropdown «Window» в каждом tab — BE/SL: preset «🔥 Since BE change (2026-05-21 19:00 UTC)» по умолчанию + Last 7/14/30/60/90 days + Custom timestamp; MFE: дефолт «📌 Since baseline» (тот же что был) + опция «🔥 Since BE change» + Custom. Response несёт `window_mode` + `since` для header'а. Bad timestamp → 400 (защита от SQL injection в interpolated value). Helper `_validate_iso_ts()` в dashboard_api_v3.py перед /api/v2/be-compare.

**Связь since с торговлей:** since влияет ТОЛЬКО на цифры/рекомендации, не на бот напрямую. Торговля меняется только при нажатии Apply (MFE → tp_ratios/distribution в JSON без рестарта; BE → be_activation/offset + restart bybit-tradingbot). Без Apply — никакого эффекта. since защищает Apply от срабатывания на устаревшей эпохе данных (confidence=insufficient_data → Apply disabled).
