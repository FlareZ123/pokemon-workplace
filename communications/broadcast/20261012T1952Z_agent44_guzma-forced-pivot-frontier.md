# Agent44 -> all: Guzma forced own-pivot can reverse immediate KO value

2026-10-12. New source-grounded tactical frontier at results/tests/guzma_forced_pivot_frontier/ (module tools/guzma_forced_pivot.py). Independent event-order vs algebraic regression covers 49,140 abstract one-turn board/capability configurations; Windows CI 38300164719 passed.

Guzma's successful opposing gust compels an *own* Active swap. Without an additional own-switch action, Boss is immediately stronger in 744 abstract states, Guzma in 15,624, tied in 32,772. Representative three-Prize witnesses: own Active can KO opponent Bench but own Bench cannot => Boss3/Guzma0; own Bench can KO but own Active cannot => Boss0/Guzma3.

Allow one freely playable Switch Item in the same turn and Boss/Guzma maximum immediate Prize values agree in all 49,140 states. Held Switch under Item lock returns exactly to the no-Switch frontier. This is a **one-turn abstract capability proof** only, not metagame frequency or deck win-rate evidence.

Competitive relevance: Aichi champion Shadow Rider has 1 Guzma, runner-up Vileplume 2, fifth Mew/Genesect 2. Current deck pages should remain unchanged; this study is an additional caution when simulating or optimizing those lists. Owner requested new atomic tests live under results/tests/ and no oversized root results index. This follows that policy.

High-value next work: implement real attacker Energy/retreat payment and persistent lock/ability state into the forced pivot, then evaluate concrete board snapshots and possible Guzma/Boss counterfactual swaps in a deck-specific experiment.
