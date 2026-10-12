# Twinleaf random shuffle bias

Pinned upstream `3348ebdc898f175a2ed8f999133cd13d1afd01f5` has a biased random index in `ptcg-server/src/game/bots/bot-arbiter.ts`: `Math.min(n-1, Math.round(Math.random()*n))`, with full-deck arbitrary swaps. Exact two-card enumeration gives identity probability **3/8** and reversal **5/8**; uniform is **1/2** each. The full three-card probabilities are 1/9, 13/108, 7/36, 5/27, 11/54 and 5/27 rather than 1/6 each.

Research-side `simulation/twinleaf/hooks/uniform-random-shuffle.cjs` subclasses the compiled arbiter with backward Fisher-Yates without editing upstream. `test-uniform-random-shuffle.cjs` exhaustively tests six three-card RNG choice paths, plus edge cases. Native tournament probe and setup use the hook, and match metadata identifies the version `research_uniform_fisher_yates_v1`.

This fixes the declared random shuffle in research harnesses only. Original biased and corrected runs must be treated as different experiment conditions. Twinleaf card semantics and SimpleTacticsAi's competitive strength remain separate unvalidated assumptions.
