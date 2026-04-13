---
name: Backtest findings and parameter sensitivity
description: Key findings from parameter sweeps on CONS strategy — what works, what doesn't, the spike filter result and its limits
type: project
originSessionId: 3c5941a8-e584-46d0-a8e0-72ab5293d0b2
---
Results of backtest parameter sweeps run 2026-04-10 on historical Binance 5m klines (with real taker buy/sell split) and Bybit daily klines (for ATR), strategy=CONS, atr_multiplier=0.15.

## Headline finding — spike filter looked amazing on BTC+ETH but doesn't generalize

**On BTC+ETH alone, 2026-01-01 → 2026-04-10 (3.3 months):**
- `spike_ratio=2.0` (current live): −36% total PnL
- `spike_ratio=6.0`: **+42% total PnL**, WR 39%, 251 trades

Raising the spike filter from 2 to 6 looked like a magic bullet. We saw wins that scaled better-than-linearly with time (March was worst month), suggesting a real edge.

**On the top 100 Bybit pairs (tier_1_top), 2025-10-10 → 2026-04-10 (6 months):**
- Processed 84 of 101 symbols (17 skipped because not on Binance futures)
- Mean PnL/symbol: **−13.08%**
- Median PnL/symbol: **−9.39%**
- Winners: 28 (33%) / Losers: 56 (67%)
- Stdev across symbols: 30% — enormous dispersion

**BTC+ETH was not representative.** The strategy has uneven edge by symbol. Top winners were APRUSDT (+61%), ACHUSDT (+28%), DYMUSDT (+26%), AI-related tokens and newer listings. Top losers were DYDXUSDT (−142%), CRVUSDT (−118%), CELOUSDT (−101%) — older large-caps with very high trade counts (300-500 trades over 6 months).

**Why:** The high-volume worst performers generated far more signals than the winners (DYDX 515 trades vs APRUSDT 78 trades in the same window). spike=6 *should* filter extremes, but on pairs with naturally high 5m volume variance the spike filter triggers too often, and each trigger has only 25-40% WR with the tight ATR × 0.15 stop — the losses compound.

## Secondary findings

### atr_multiplier sensitivity (BTC+ETH, 1 month)
Widening the stop (0.15 → 0.30) improves WR (25.9% → 34.7%) but worsens total PnL (−36% → −60%). Reason: TP ladder is relative to SL distance (1R/3R/5R), so widening SL pushes TPs proportionally further, and most trades timeout at breakeven rather than reaching TPs in 24h. Stop width alone is not the lever.

### max_bars 24h vs 48h
Doesn't help. 48h window produces nearly identical or worse PnL. Trades that would have timed out at 24h mostly end as SL within 48h. The strategy either wins fast or loses.

### tp_scale (scalar on TP ladder)
Shrinking TPs (tp×0.5) gives small PnL improvement (~5% on 1 month). Default (tp×1.0) is close to optimal when paired with a good spike filter.

## Live implications

**Do NOT change `signal_bot_config.json` spike_ratio to 6.0 based on the BTC+ETH result alone.** It would likely be a net loss across the full 301-symbol trading list.

Realistic paths to profitability:

1. **Symbol whitelisting.** Backtest each of the 301 symbols, pick the top-N consistently profitable at spike≥6, trade only those. Rebalance monthly. Probably 20-40 symbols make the cut.
2. **Per-symbol parameters.** Tune spike_ratio per symbol based on its volume variance. High-variance pairs (CRV, DYDX) need higher threshold; quiet pairs might work at lower.
3. **Different signal criteria entirely.** The current combination (volume×spike×trend×B/S) may not have enough edge. Consider adding ATR-relative volume filtering, or order-book imbalance from publicTrade rather than just 5m bucket aggregates.

**Why:** Documents load-bearing parameter-sensitivity results so I don't repeat the mistake of recommending spike=6 as a universal fix.

**How to apply:** When proposing strategy changes, always sanity-check on a wide symbol set before promoting to live. BTC+ETH alone is not a representative sample.
