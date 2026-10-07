# Devolution and identity conservation

This result checks the reverse direction of Pokémon-card materialization.

A persistent Pokémon object begins with two physical cards in its stack: Bulbasaur and Ivysaur. Both are represented by materialized instances in the identity ledger.

The board transition `devolve_top()` removes the highest Evolution card and keeps the lower-stage Pokémon object in play. It also marks ordinary evolution unavailable for that turn and accepts the lower stage's resolved Retreat Cost as an input.

The identity transition then moves the removed Ivysaur instance out of the board relation and dematerializes it back into an exchangeable hand count.

The regression verifies that:

- the exact physical Ivysaur instance leaves the stack;
- the Bulbasaur physical instance stays bound to the same Pokémon object;
- total card counts are conserved;
- the Ivysaur class returns to the hand count;
- a Basic-only stack cannot be devolved by this transition.

This isolates the identity semantics from the later Knock Out check that may be required when retained damage exceeds the lower stage's remaining HP.

Implementation: `tools/board_position_kernel.py`  
Regression: `results/devolution_materialization/reproduce.py`
