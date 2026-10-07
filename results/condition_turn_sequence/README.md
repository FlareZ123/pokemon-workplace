# Skipped Pokémon Checkup delays Special Condition transitions

## Question

What happens to Special Conditions when an extra-turn effect explicitly skips
Pokémon Checkup?

Implementation: `tools/condition_turn_sequence.py`  
Regression: `results/condition_turn_sequence/reproduce.py`

## Concrete card anchor

The supplied Expanded card database contains Origin Forme Dialga VSTAR
`swsh10-114`. Its **Star Chronos** attack says:

`Take another turn after this one. (Skip Pokémon Checkup.)`

The regression reads that exact card record from
`resources/cards/en/swsh10.json`.

## Finding

A skipped Checkup is a real missing state transition.

The regression starts player A's turn with a Poisoned condition already on A's
Active Pokémon. A ends the turn with the represented Star Chronos boundary:

1. the attack ends A's turn;
2. an extra A turn is queued;
3. Pokémon Checkup is skipped;
4. no Poison damage-counter event occurs;
5. the Poisoned condition remains present into the extra turn.

After A's extra turn ends normally, Pokémon Checkup occurs and the ordinary
Poisoned transition finally places one damage counter.

A simulator that automatically processes Special Conditions whenever a turn
ends would incorrectly damage the Pokémon before the extra turn.

## Representation

`advance_with_conditions()` composes two existing authorities:

- `turn_sequence_kernel.advance_turn()` decides whether the boundary actually
  contains Pokémon Checkup and which player continues;
- `timed_special_conditions.resolve_basic_checkup()` runs only when the first
  layer says Checkup occurs.

The wrapper also advances a monotonic turn serial on every real turn, including
an extra turn. The serial is separate from whether Checkup occurs.

This distinction matters for temporal statuses such as Paralysis: elapsed turns
and executed Checkups are different state dimensions.

## Architectural consequence

Turn-end handling should not directly invoke a status resolver.

The safer flow is:

`turn ends -> determine boundary type -> maybe Pokémon Checkup -> resolve status/effects -> start next turn`.

This makes card text such as Star Chronos and Yoga Loop a boundary mutation
rather than a special case inside every Special Condition implementation.

## Validation

The regression verifies:

- the exact Star Chronos text in the supplied database;
- same-player continuation after the extra-turn attack;
- `pokemon_checkup_occurs == False` at that first boundary;
- Poison remains present with zero Checkup counter events;
- the extra turn increments the turn serial;
- a normal boundary after the extra turn processes Poison once.

## Limits

The example uses Poison because it is deterministic. Burn and Asleep require
coin outcomes, while Paralysis additionally uses owner-turn age.

The wrapper resolves one modeled Pokémon's status state. A full match kernel
must run the same boundary over every relevant Active Pokémon and then compose
Checkup effects and the deferred Knock Out batch.

## Next useful work

The strongest next case is Paralysis across a skipped Checkup. It can distinguish
"an owner turn has elapsed" from "the recovery Checkup actually occurred" and
therefore test whether turn-age alone is sufficient or whether the status needs
an explicit pending-recovery state.
