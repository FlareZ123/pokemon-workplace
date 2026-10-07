# Special Energy movement conservation

## Question

What happens to physical card identity when an effect moves a restricted Special
Energy to a Pokémon that cannot legally have that Energy attached?

Implementation: `tools/special_energy_move_conservation.py`  
Regression: `results/special_energy_move_conservation/reproduce.py`

## Rule and card basis

The Advanced Player's Rulebook states that an effect may move a Special Energy
to a Pokémon to which that Energy cannot be attached. In that case the Special
Energy is removed from the source Pokémon and discarded rather than becoming
attached to the chosen destination.

The repository's `xy6-97` Double Dragon Energy is a concrete Expanded-legal
example. Its card text restricts attachment to Dragon Pokémon and says to
discard it if it is attached to anything else. It also provides two Energy at a
time while legally attached to a Dragon Pokémon.

## Conservation model

Destination legality is deliberately resolved upstream. The adapter receives
that result as `destination_accepts_card`.

- If true, it delegates to the existing physical Energy-movement transition.
  The same `instance_id` changes holders and remains materialized.
- If false, it removes that exact physical Energy from the source, moves its
  ledger instance to discard, then dematerializes it into the exchangeable
  discard count.

In both branches, per-card-class totals are invariant.

## Regression

The regression materializes one `xy6-97` Double Dragon Energy copy and binds
it to a Dragon Pokémon.

For a legal move to another Dragon Pokémon:

- the source loses the attachment;
- the target receives the same physical `dde-a` instance;
- the two-unit representation is preserved;
- the identity ledger updates only the attachment holder.

For a move whose chosen destination is a non-Dragon Pokémon:

- the source loses `dde-a`;
- the destination never receives it;
- the materialized instance is removed;
- the Double Dragon Energy card class gains one discard-pile copy;
- total copies remain exactly one.

## Finding

A card movement edge and a successful attachment edge are distinct operations.

For restricted Special Energy, selecting a destination can be legal while the
post-move attachment relation is impossible. A transition model that represents
"move Energy" as an unconditional holder reassignment will preserve an illegal
board state.

## Scope

This adapter does not infer attachment legality from card text, Pokémon type, or
other effects. It consumes a resolved legality predicate. Building that predicate
belongs in the Energy/card-text semantic layer.

Replacement effects, effects that redirect the discarded Energy to another
zone, and simultaneous multi-Energy moves remain outside scope.
