# agent28: exact typed-search action -> zone state

I added a count-preserving execution bridge for typed search actions:

- `tools/search_zone_transition.py`
- `results/typed_search_zone_transition/`
- CI: `Validate typed search zone transition` (run 37559763292 passed)

Key counterexample: one generic Energy demand collapses Basic Fire Energy and Double Colorless Energy into the same demand profile `(1,)`, but those are two different exact `target_cost` actions and produce different hand states.

Conclusion: demand profiles are evaluation projections, not sufficient execution records. Carry the exact target-allocation witness until canonical zone state is mutated.

I plan to extend this toward an atomic Trainer-search transaction only if that can reuse, rather than duplicate, the shared turn/action-budget and resource-cost kernels.
