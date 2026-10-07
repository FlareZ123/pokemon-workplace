# Retreat Energy normalization order

## Question

When a holder changes state, two Special Energy mechanisms can become stale at
once:

- an attachment may cease to be legal and need to self-discard;
- a surviving attachment may provide a different number of Energy units.

Which order should a Retreat planner use?

## Result

`tools/retreat_energy_normalization.py` composes the two validated layers into
one deterministic preparation step:

1. revalidate holder-restricted Special Energy and discard illegal physical
   attachments;
2. refresh the current Energy-unit counts of the surviving dynamic providers.

The result records both physical restriction discards and unit-count refreshes.

## Why order matters

Provider refresh must not breathe life back into a card whose own attachment
restriction has already failed.

The regression uses a stale Triple Acceleration Energy on a Basic Pokemon. Its
stored snapshot still contains three Energy units, which would be sufficient
for Retreat Cost 3 in the low-level payment solver. Normalization removes the
physical Energy card before any provider refresh, moves its card-class count to
discard, and makes that Retreat payment impossible.

A separate Ignition Energy witness on a Stage 1 holder survives attachment
validation, refreshes from one represented unit to three, and can then pay
Retreat Cost 3.

## Architectural implication

Attached Energy needs at least three conceptual layers:

1. **physical identity**: which exact Energy card remains attached;
2. **attachment validity**: whether that physical relation is still permitted;
3. **current provider state**: how many Energy units the valid card supplies.

Retreat payment belongs downstream of all three.

This ordering generalizes beyond Retreat. Attack-cost evaluation and
Energy-discard effects can suffer the same stale-state failures when they read
an attachment snapshot without first normalizing its current legality and
provider behavior.
