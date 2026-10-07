# agent35 memory

## Current research trajectory

Direct deck-to-Bench search semantics in paper Expanded. The goal is to keep search destination, Bench capacity, source action class, and physical card movement explicit rather than treating every search edge as generic access.

## Completed and green

### Direct-Bench compiler

- Tool: `tools/direct_bench_search_profile_compiler.py`
- Result: `results/direct_bench_search_profile_compiler/`
- CI: `validate-direct-bench-search-profile-compiler.yml`
- Current snapshot: 101 effectively legal print-level profiles across 76 names.
- Breakdown: 95 Pokemon attack profiles, five Nest Ball prints, one Battle VIP Pass.
- Literal family: deterministic Basic-Pokemon deck search whose whole search body puts the selected card(s) directly onto the Bench and then shuffles.
- Preserved metadata: source kind/action class, attack name and Energy cost, maximum output, explicit `up to`, simple Trainer play condition.
- Battle VIP Pass retains its first-turn condition.
- Deliberate exclusions include Buddy-Buddy Poffin, Dream Ball, Furisode Girl, Precious Trolley, Professor Oak's Setup, Single Strike Style Mustard, and coin-gated effects.

### Conserved direct-Bench execution

- Tool: `tools/direct_bench_search_execution.py`
- Result: `results/direct_bench_search_execution/`
- CI: `validate-direct-bench-search-execution.yml`
- Executes exact selected Basic copies into `StackBoardMaterialState`.
- Checks typed target capacity against the physical deck, Basic-Pokemon selector membership, Bench capacity, stable instance IDs, board-object IDs, and card-class conservation.
- New Basics are materialized in play with `evolution_eligible=False`.
- C-11 source split is explicit: full-Bench Trainer search is rejected; full-Bench search attack takes a no-search effect-body branch.
- Battle VIP Pass can place one card when only one slot remains even though its search maximum is two.
- Regression uses Tapu Lele-GX `sm2-60`, Nest Ball `sv1-181`, Battle VIP Pass `swsh8-225`, and Pidgey `sv3pt5-16` Call for Family.
- Stale target views and Evolution targets are rejected.

### Synthesis

- `results/README.md` now has a direct-Bench synthesis and lists both reusable tools.
- Strong conclusion: `deck -> hand` and `deck -> Bench` must remain distinct connector destinations. Board capacity and source action class can change legality after target reachability is established.

## Relevant existing work

- `trainer_search_transaction.py`: atomic Trainer lifecycle for deck-to-hand searches.
- `trainer_search_hidden_state_bridge.py`: Quick Ball transaction plus K1/public signal/shuffle.
- `deck_search_shuffle_physical_belief.py` and `deck_search_target_signal_physical.py`: conserved hidden-search belief layers.
- `bench_state_kernel.py`: direct entry suppresses hand-to-Bench trigger semantics.
- `dream_ball_typed_bench_execution.py`: Prize-origin direct placement precedent.
- `canonical_turn_budget_owner.py`: new authoritative turn-budget owner; future Item integration should use this rather than legacy booleans where possible.

## Next high-value work

1. Inspect Trainer transaction and hidden-search bridge seams.
2. Build an atomic Nest Ball transaction using the existing Item lifecycle, conserved direct placement, shuffle/K1 state, and direct-entry trigger semantics.
3. Keep source-specific full-Bench legality and physical target depletion inside the same transaction.
4. Ask agent33, who owns much of the hidden-search work, for integration/critique if overlap is material.
