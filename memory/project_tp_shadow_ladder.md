---
name: project-tp-shadow-ladder
description: TODO — мониторинг «куда доходят сигналы» после перехода на 100% close TP1=2R. Shadow ladder + MFE peak tracker + weekly auto-promote. Дизайн для будущей реализации.
metadata: 
  node_type: memory
  type: project
  originSessionId: cbd11597-bb85-4f31-a1c0-60ce301b7c11
---

**Проблема:**
С 2026-05-21 все стратегии закрывают 100% позиции на TP1=2R. Это убирает «царапину» TP1→BE, но создаёт слепую зону: мы НЕ знаем, дошла бы цена до 2.5R / 3R / 4R / 5R. Если рынок поменяется (volatility ↑, тренды длиннее), оптимальный TP подвинется выше — но мы не увидим этого без данных.

**Вариант A — Shadow ladder в DB (рекомендую как первый шаг):**
- На каждый сигнал TradingBot открывает реальный paper-trade (full TP1=2R close) + shadow row в `simulated_trades` с флагом `is_shadow=1` и полной лесенкой (TP1=2R, TP2=3R, TP3=4R, TP4=5R, TP5=8R) на ту же qty.
- Shadow ничего не делает с wallet, ничего не отправляет в Bybit — только треккает price-monitor и пишет close_reason.
- В dashboard добавить toggle «show shadow stats» — функционал TP funnel рисуется на shadow data, реальные стратегии остаются простыми.
- **Плюсы:** zero risk, полная funnel-картинка, дёшево реализовать (≈+50 строк в order_executor + price_monitor).
- **Минусы:** удвоение objects в БД (но не trades; lightweight).

**Вариант B — расширить существующий MFE-tracker:**
- `peak_pnl_pct` уже пишется (`project_mfe_calibration.md`). Расширить: после закрытия trade продолжать треккать peak ещё T=12h (или до timeout), записывать `peak_after_close_pct`.
- Дешевле shadow (без отдельных rows), но даёт только max — не funnel-распределение по уровням.
- **Плюсы:** минимум кода, использует существующую инфраструктуру.
- **Минусы:** не показывает «процент сделок дошедших до уровня X» — только средние/median peaks.

**Вариант C — четвёртая виртуальная стратегия «MONITOR»:**
- Дублирующая стратегия которая на каждый сигнал создаёт полноценный paper-trade с 5-level ladder.
- По сути — Вариант A, но через основной pipeline, без отдельного флага.
- **Плюсы:** zero code changes — просто новая запись в strategy_parameters JSON.
- **Минусы:** дублирует сделки в funnels всех стратегий, путает statistics_manager. Не делать.

**Вариант D — Auto-tuner (после A или B, не раньше):**
- Weekly cron: читает shadow/MFE данные за 30 дней.
- Если на 50+ сделках median MFE peak > 1.5×current_TP1 (то есть рынок ушёл бы дальше) — рекомендует поднять TP1 на 0.25–0.5R.
- Если WR на текущем TP1 ≥ 55% и Sharpe ≥ 0.5 на 50+ закрытых — рекомендует поднять per-trade risk на 10–20%.
- Применение — через `/api/settings/*` (тот же chain что [[project-dashboard-apply-chain]]).
- Через TG-нотификацию + governor: Артём может pause или approve вручную, потом auto-apply (как `project_trading_state_softgate`).

**Рекомендованный путь:**
1. Сначала Вариант A (Shadow ladder). 1–2 недели данных накопить.
2. Параллельно Вариант B (peak_after_close в MFE) — почти бесплатное расширение.
3. Через месяц — Вариант D auto-tuner с governor, читающий обе data sources.

**Зависимости / риски:**
- Shadow row не должен попадать в P&L stats реальных стратегий — нужен жёсткий guard в `stats_manager_v3` и v2 dashboard endpoints (`is_shadow=1` исключается из net/PF/WR).
- Auto-tuner апплит настройки — Артём боится GA-overfit ([[project-ga-under-review]]). Для auto-tuner ОБЯЗАТЕЛЬНО: small step (≤0.5R), min sample 50, weekly cooldown, governor + manual approve по умолчанию.
- Не запускать auto-tuner до того как накопим shadow data на ≥30 дней.

**Когда вернёмся:** после 2026-06-01 — будет 10+ дней свежих данных на новых настройках TP1=2R.
