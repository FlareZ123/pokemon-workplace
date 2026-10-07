# One-card Energy disruption compiles into conserved attachment removal

## Question

Which common opponent Energy-discard wordings can be compiled without collapsing
target geometry, Energy type, or coin gating?

This result follows the corpus-first inventory and accepts only complete effect
bodies that discard exactly one Energy card.

Implementation:
- tools/energy_disruption_profile_compiler.py
- tools/energy_disruption_executor.py

Regression: results/energy_disruption_profile_compiler/reproduce.py

## Compiled dimensions

EnergyDisruptionProfile preserves:

- any Energy versus Special Energy;
- opponent's Active versus a selected opponent Pokémon;
- deterministic versus heads-gated discard;
- Trainer versus attack source;
- attack name/cost/damage when the source is an attack.

Both historical phrasings "from" and "attached to" normalize to the same
mechanical profile.

The compiler rejects multi-Energy discard, all-Energy discard, Energy-type
specific discard, before-damage clauses, additional consequences, self-costs,
and other compound text.

## Conserved execution

The executor receives the opponent-side StackBoardMaterialState and one exact
Energy instance to discard after all profile constraints pass.

The attachment is removed from the Pokémon, the same physical identity is
detached into discard, and ordinary execution dematerializes it into the
exchangeable discard count. Card-class totals remain invariant.

Special-Energy profiles require the caller to identify which materialized Energy
instances are Special Energy. That metadata stays outside the generic attachment
record for now.

## Hammer witness

A target Pokémon carries one Basic Energy and one Special Energy.

A Crushing Hammer-shaped profile:

- tails leaves the state unchanged;
- heads can discard the exact Basic Energy instance.

An Enhanced Hammer-shaped profile rejects the Basic Energy and discards the
Special Energy instance.

The regression also requires real compiled Crushing Hammer and Enhanced Hammer
profiles from the effectively legal bundled snapshot.

## Why quantity is restricted to one

The rulebook includes Energy cards that can provide multiple units of Energy.
An instruction to discard two or more Energy can therefore require semantics
about provided Energy units rather than simply selecting two physical cards.

This first island avoids that ambiguity by compiling only one-Energy
instructions.

## Strategic consequence

Energy denial is stateful resource denial rather than a generic tempo score.
Discarding one exact attachment can remove an attack route, retreat payment, or
future movement option. The conserved executor leaves those downstream
consequences available to the existing board and action-budget layers.

## Limits

The compiler does not yet model typed Energy requirements, multi-unit Special
Energy payment semantics, or effects that choose several Energy cards.

Coin gating is resolved by a caller-supplied result. Probability policy belongs
above this deterministic mechanics transition.

Regional limits of the English card snapshot remain unchanged.
