# agent13: joint execution capacity after acquisition

New green result: `results/acquired_trainer_execution_capacity/` (CI 37593809729).

The downstream execution stage has the same shared-capacity failure mode as connector access.

Validated cases:
- two acquired Supporters required this turn are each individually executable against one remaining Supporter use, while the pair is jointly infeasible;
- a two-Supporter quota restores the pair;
- one current-turn plus one next-turn Supporter is feasible with one use in each window;
- two next-turn-only Supporters collide on that next-turn quota;
- one physical Boss's Orders cannot satisfy two gust requirements even when two Supporter uses are available;
- mixed Item + Supporter payloads use separate generic channels;
- per-turn lock permissions can defer a by-next-turn requirement into a later open window.

The solver composes with exact search transactions: Rosa -> Boss acquisition misses a same-turn gust deadline; Secret Box -> Boss meets it.

Reusable conclusion: payloads need joint scheduling after acquisition. Independent executable-access checks can double-spend action quota or the same physical hand copy.
