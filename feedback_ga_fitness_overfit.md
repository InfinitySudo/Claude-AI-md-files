---
name: GA Fitness Overfit Guards
description: Fitness function constants that prevent narrow/single-symbol overfit corners from winning evolution
type: feedback
originSessionId: 7da703ef-c9f9-47d8-9238-52d53b1a1d23
---
GA fitness (scripts/ga_optimizer.py) has two anti-overfit guards introduced 2026-04-21:

- `MIN_TRADES_REQUIRED = 50`: below this per strategy, fitness is clamped to a gradient `-100 + n*2` that cannot outcompete real runs. Prevents "22 trades, 100% WR" corners the 2026-04-20 run converged on (all top-3 produced 0 test trades).
- `MIN_TRADES_FULL = 200`: trade_factor ramps linearly from 0 at MIN_TRADES_REQUIRED to 1.0 here. Replaces old `n/30` which was 0.73 at n=22.
- `MIN_SYMBOL_COVERAGE = 0.15`: if trades come from <15% of the symbol universe, coverage penalty squares the deficit. Prevents param sets that only fire on 5/195 coins.

**Why:** 2026-04-20 GA produced params that fired on 22 symbols during TRAIN with 100% WR and 0 trades on TEST — classic overfit. Old fitness rewarded it because `trade_factor` wasn't strict enough and there was no diversity check.

**How to apply:**
- `_run_strategy` returns `(pnls, symbols_with_trades)`; `_compute_fitness(arr, symbols_with_trades, symbols_universe)`. Both `evaluate()` and `walk_forward_evaluate()` pass these.
- When tuning these constants, run the 5-case synthetic test at the bottom of the fitness function (last-run corner should come out below -90, concentrated=5-symbol should be ~30× worse than 40-symbol with same PnL).
- If a legit universe has <50 live trades per strategy over train period, lower MIN_TRADES_REQUIRED rather than removing the guard — it's load-bearing.
