# Causal state owner for continuous Ability locks

## Question

What is the smallest reusable state layer that can combine the verified setup
precedence and the verified midgame established-source ruling without turning
either into an unsupported universal rule?

The answer is a causal wrapper around the history-free dependency graph.

## Model

`tools/ability_lock_causal_state.py` owns an `AbilityLockCausalState` with:

- the current `AbilityLockResolution`;
- a basis describing how that resolution was obtained.

The current basis values are `snapshot`, `setup_first_player`,
`verified_established`, and `unresolved`.

The dependency graph remains authoritative for current source geometry. The
causal owner adds precedence only where evidence exists.

## Initialization

`initialize_snapshot_lock_state` uses the ordinary dependency graph. Acyclic
source graphs resolve directly.

`initialize_setup_lock_state` additionally applies the official first-player
precedence rule for the verified reciprocal two-Active setup family.

## Event advance

`advance_lock_state` recomputes the current dependency graph after each board
or event boundary.

If the graph is acyclic, snapshot resolution becomes authoritative again.

If the source graph is still the same verified cyclic graph, the already
resolved winner persists and its target overlay is recomputed on the new board.
This allows ordinary targets to enter or leave without forgetting precedence.

If a previously one-way Garbotoxin -> Cursed Land relationship gains the
verified reverse edge after Garbodor becomes damaged, the established-precedence
resolver carries Garbotoxin forward.

Other cyclic transitions remain unresolved.

## Regression

The regression covers two independent histories.

First, Empoleon V wins the official setup precedence over Wobbuffet. A Magnezone
is then added as an ordinary target. The source graph is unchanged, so the
setup winner persists and the new Magnezone remains outside Bide Barricade
suppression.

Second, undamaged Tool-attached Garbodor initially suppresses Ting-Lu ex in an
acyclic snapshot. Adding damage to Garbodor creates the official reciprocal
Cursed Land cycle, which resolves to established Garbotoxin. A new ordinary
target can then enter while that source graph remains unchanged, and the
Garbotoxin overlay expands to suppress it. Removing Garbodor's damage returns
the graph to an acyclic snapshot state.

## Architectural implication

The effective lock layer is a derived causal state, not a permanent mutation of
Pokemon objects. Canonical physical boards stay unchanged while suppression is
recomputed from current geometry plus the smallest verified precedence history.

This makes downstream systems such as action-quota derivation consume one
effective suppression overlay without owning their own lock history.

Regression: `results/ability_lock_causal_state/reproduce.py`.
