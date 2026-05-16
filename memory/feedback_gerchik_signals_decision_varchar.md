---
name: gerchik-signals-decision-varchar
description: "gerchik_signals.decision = varchar(40) — никогда не пиши туда полный reason, иначе ВСЕ skip-сигналы тихо валятся в log_signal с overflow"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c9644492-6498-4771-8705-09a9325b061e
---

В таблице `gerchik_signals` (Postgres `trading_bot_v3`) колонка `decision` ограничена `varchar(40)`, индексирована (`idx_gerchik_signals_decision`). Колонка `skip_reason` рядом — `text`, без лимита.

**Правило:** в `decision` пиши только короткую категорию вида `opened` или `skipped:<category_prefix>` (категория = `check.reason.split(':',1)[0][:32]`). Полный текст причины — в `skip_reason`.

**Why:** До 2026-05-16 в [[project-gerchik-bot]] `signal_engine.py:219` стояло `decision = f"skipped:{check.reason}"`, и `check.reason` обычно вида `counter_htf_trend: SHORT требует обоих TF=down, got 4H=down, D=up` — это далеко за 40 символов. Postgres валил INSERT с `value too long for type character varying(40)`, журнал `gerchik.journal` плевался ERROR'ом, но `log_signal` ловил исключение и возвращал None — то есть полная тишина в БД при работающем агенте. За 36 часов 0 строк в `gerchik_signals`, при том что в systemd журнале десятки skip-событий — диагностируется только перекрёстной сверкой journal vs DB.

**How to apply:**
- Если меняешь формат `decision` или добавляешь новые причины skip — держи итоговую строку ≤40 символов.
- Если хочется писать туда богатые значения — расширяй колонку (`ALTER TABLE gerchik_signals ALTER COLUMN decision TYPE varchar(80)`), но учти что она индексирована и используется в фильтрах дашборда.
- Проверочный SQL на регресс: `SELECT COUNT(*) FROM gerchik_signals WHERE detected_at > NOW() - INTERVAL '1 hour'` — должно быть >0 в активные торговые часы.
- Связано с тихим swallow'ом: см. [[feedback-query-write-swallow]] (та же семья багов — INSERT гасится в try/except и пропадает без следа).
