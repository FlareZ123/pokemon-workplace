# Replacement-aware discard safety under Prize uncertainty

## Question

If a current required copy can be restored only when another copy is not Prized, how should discardability behave before and after the first full deck inspection?

It should be belief-weighted before exact Prize knowledge and state-deterministic afterward.

Implementation: `tools/belief_weighted_discard_policy.py`  
Reproducer: `results/belief_weighted_replacement_safety/reproduce.py`

## Composition

This result composes:

- `PrizeBelief` for grouped Prize-composition uncertainty;
- `continuation_discard_policy.py` for exact discard choices and endpoint filtering;
- Arven from the compiled multi-output Trainer-search family;
- `trainer_search_transaction.py` for conserved replacement retrieval.

For each Prize-composition world, a state factory places the represented replacement copies into deck or Prize according to that world. The same exact discard decision is then evaluated against legal continuations.

The final safety probability of a discard selection is the total belief mass of worlds where at least one continuation restores the endpoint.

## Concrete decision

The current hand contains:

- one required TM: Evolution;
- one ordinary fodder card;
- Arven.

The endpoint requires one TM: Evolution in hand.

The player must discard exactly one card.

The two candidate choices are:

- discard fodder;
- discard the current TM: Evolution.

Discarding fodder preserves the current TM immediately, so it is safe in every Prize world.

Discarding TM relies on Arven searching another copy from the deck.

## K0 with one replacement copy

Model one replacement TM among a 53-card unknown pool with six Prize cards.

The replacement is unprized with probability:

`C(52, 6) / C(53, 6) = 47/53 = 88.679245283%`

Therefore:

| Discard | Endpoint-safety probability |
| --- | ---: |
| fodder | 100% |
| current TM | 88.679245283% |

The TM discard is mechanically selectable in every world. Its strategic safety changes with hidden Prize composition.

## K1 collapse

After exact Prize composition is learned:

- if the replacement TM is known unprized, discarding current TM is safe with probability 1;
- if the replacement TM is known Prized, discarding current TM is safe with probability 0.

The same current hand therefore receives a different discard classification solely from information state.

This is a direct bridge between the human K0/K1 idea and continuation-aware DCI.

## Redundant replacement copies

With two replacement TM copies in the same 53-card unknown pool, the current TM discard fails only if both replacements are Prized.

The exact safety becomes:

`1 - C(2, 2) C(51, 4) / C(53, 6) = 98.911465893%`

Redundancy sharply raises recovery safety, while still leaving a nonzero catastrophic Prize configuration.

This is the same multi-Prize-collapse principle applied to future discard recovery.

## Finding

Discardability under hidden information has two distinct layers:

1. **world-conditional legality:** does this exact discard have a conserved restoring continuation in the actual Prize world?
2. **belief-level risk:** how much probability mass currently lies on worlds where that continuation exists?

A scalar DCI can be informed by the second quantity, while exact execution must still obey the first.

K1 does not merely improve search sequencing. It can change whether a payload copy is strategically acceptable to discard.

## Limits

The example models replacement copies as one grouped Prize class and assumes Arven is available in hand with an unused Supporter quota.

It does not yet include opponent interaction, partial Prize observations, alternative recovery lines, or utility differences between success and failure.

The safety probability is not itself an optimal decision threshold. A risk-neutral policy, tournament match context, alternative lines, and failure severity can all change whether an 88.68% or 98.91% recovery probability is acceptable.

## Next useful work

A natural extension is to value information before the discard decision.

The planner can compare:

- commit under K0;
- spend a search or inspection action to reach K1 first;
- preserve the current copy and choose a lower-risk line.

That would assign a direct tactical value to deck inspection when exact knowledge changes the safe-discard witness family.
