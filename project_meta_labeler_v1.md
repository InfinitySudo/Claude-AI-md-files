---
name: Meta-labeler V1 — XGBoost binary classifier для signal-quality
description: Активен 2026-05-08, AUC test 0.728, shadow mode (log_only=true); масштабирует position size DOWN-only по P(profitable)
type: project
originSessionId: 6d88615c-040f-460e-b3c6-b231427e8dab
---
**Что:** XGBoost binary classifier предсказывает `P(profitable | signal_features)`. Position size в `risk_manager_v3.calculate_position_size` скейлится **только вниз** (P≥0.7 → 100%, P<0.7 → linear до floor 0.3). Никогда не boost'ит выше base.

**Why:** Не все сигналы равны (TREND 100% SL streak, CONS TP1 41% hit но 2.4% close). ML фильтрует худшие, не отказываясь от них (полная статистика + меньший риск). Lopez de Prado meta-labeling pattern.

**Training:**
- Скрипт: `scripts/ml/build_meta_labeler_dataset.py` (VPS, postgres) → `scripts/ml/train_meta_labeler.py` (PC1, xgboost CPU)
- Данные: 808 closed paper trades 14d, JOIN signals_queue × accepted_signals × simulated_trades
- Features (13): spike_ratio, log_volume_usd, buy_volume_pct, bs_imbalance, atr_normalized, atr_multiplier, is_long, strategy_{cons,trend,aggr}, hour_sin/cos, symbol_recent_wr_24h
- Train/test: walk-forward 80/20 sequential (не shuffle)
- **Результаты V1:** AUC train 0.866, AUC test 0.728. Calibration: P=0.7 bin → 75% actual WR (ideal). Top features: is_long, atr_normalized, atr_multiplier, hour_sin
- Floor для go-live: AUC test ≥ 0.55. V1 проходит.

**Файлы (gitignored):** `models/meta_labeler_v1.json`, `_features.json`, `_metrics.json`. PC1 path: `C:\Users\tkach\meta_labeler\models\`.

**Inference:** `src/ml_meta_labeler.py:MetaLabeler` singleton, hot-reload по mtime каждые 60s. На ошибку → P=0.5 → no scaling (fail-open).

**Settings:**
- `meta_labeling_enabled` (bool, default false) — master toggle. Сейчас FALSE (shadow only).
- `meta_labeling_log_only` (bool, default false). Сейчас TRUE (logs every prediction в `meta_labeler_predictions` table without scaling qty).
- `meta_labeling_size_floor` (0.3) — min multiplier
- `meta_labeling_active_p_threshold` (0.7) — выше = 100%

**Audit:** `meta_labeler_predictions` table (signal_id, predicted_p, applied_scale, model_version, features). Endpoint `/api/ml/status` показывает train AUC + 30d live calibration JOIN.

**Auto-retrain:** `scripts/ml/weekly_retrain.sh` + `bybit-meta-retrain.timer` Sun 04:00 MDT. Pulls fresh data from VPS → trains on PC1 → deploys только если new AUC ≥ old + 0.01.

**Promote to live (через 50+ post-baseline сделок):**
1. SQL check: `SELECT FLOOR(predicted_p*10)/10, AVG(actual_outcome) FROM ...` — должно матчить training calibration
2. Если P=0.7 bin → ≥65% live WR → `meta_labeling_log_only=false`, `meta_labeling_enabled=true`
3. Через 100+ scaled trades → если Sharpe up vs baseline V2, оставляем; иначе rollback
