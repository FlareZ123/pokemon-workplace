# Physical source identity and lifetime in copied attacks

## Question

When a copy effect obtains an attack from a physical Pokémon card and then moves that card before the copied body resolves, can the resolver identify the copy only by attack name or attack ID?

No. The source instance can be part of the action.

Implementation: `tools/attack_copy_kernel.py`  
Regression: `results/attack_copy_source_lifetime/reproduce.py`

## Concrete card families

Two legal Expanded attacks force this issue.

**Hypnotic Reign** on Malamar `sm10-119` reveals the opponent's hand, may discard a Pokémon found there, and then uses one of that Pokémon's non-GX attacks as the attack.

**Seek Inspiration** on Slowking `sv7-58` discards the top card of the user's deck and, if it is an eligible Pokémon without a Rule Box, chooses one of that card's attacks and uses it as the attack.

In both cases the physical source has already left the zone that exposed its attack by the time the selected attack body executes.

## Representation change

The copy kernel now carries source provenance for card-backed copy candidates.

For each candidate attack it can retain the exact physical `PokemonRef.card_id` values that supplied that attack. A selector may declare a required source-zone commit, such as moving the selected source to the discard pile.

The sequence is:

`discover candidate source -> choose attack -> choose exact physical source when needed -> commit source movement -> execute snapshotted attack ID`

The attack body therefore remains executable after its source leaves the lookup zone.

## Duplicate-source ambiguity

This matters even when two physical cards expose the same attack.

The regression places two opponent-hand Pokémon that both supply the same non-GX endpoint for Hypnotic Reign. Choosing only the endpoint attack is insufficient to determine which physical Pokémon must be discarded.

The kernel now rejects that under-specified state with `AmbiguousCopySource`. Supplying an exact source choice moves only that card to the discard pile while leaving the other copy in hand.

This is a small conservation requirement: effect semantics can depend on card identity even when attack semantics are identical.

## Eligibility before commitment

Source eligibility is evaluated before mutation.

The regression also verifies:

- Hypnotic Reign rejects a GX endpoint and leaves its source in hand;
- Seek Inspiration rejects a Rule Box source and leaves the top card in its original modeled zone;
- an eligible Seek Inspiration source moves to discard before the selected endpoint body completes.

## Cycle detection implication

The copy kernel now includes physical source zones in its recurrence key.

That became necessary once copy effects could mutate zones during nested execution. A cycle detector that ignored those mutations could classify a state-changing recursive path as a no-progress loop.

## Broader implication

A copy graph can use attack signatures for static reachability, while executable resolution needs a richer witness:

`attack identity + source object + source zone + selection restrictions + source commit`

This is another case where an existential edge is weaker than an executable action.

## Limitations

The small kernel models exact source identity and zone commitment for the two current discard-before-body families. It does not yet model complete hidden-information procedures, deck ordering beyond an explicit `deck_top` state, reveal permissions, ownership-specific discard piles as separate physical containers, or every source-movement wording.

Those details belong in a fuller state engine, while the source-identity requirement established here should remain.
