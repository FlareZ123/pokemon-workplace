# Materialized hand identity must count toward draw-to-N

## Question

After an exact private search target is materialized as a hand instance, can a continuation safely derive hand size from the aggregate exchangeable zone ledger alone?

No.

Implementation: tools/physical_zone_count.py
Regression: results/materialized_hand_size_continuation/reproduce.py

## Representation boundary

IdentityLedger deliberately separates exchangeable off-board copies from materialized physical instances. That is useful when one searched copy becomes exact physical truth.

Hand size is a physical zone metric. It must sum both representations.

The new physical_zone_count helper counts exchangeable zone multiplicity plus materialized instances in that zone. physical_hand_size is the hand-specific projection.

## Atomic Computer Search continuation

The regression extends the exact Computer Search transaction with one Crobat V already in hand.

After Computer Search resolves:

- Crobat V remains exchangeable in hand;
- private searched X is a materialized hand instance.

Physical hand size is therefore 2, while the exchangeable hand count is only 1.

Next, Crobat V is materialized from hand and put into play. The remaining physical hand contains the private X instance:

- physical hand size = 1;
- exchangeable hand count = 0.

A Dark Asset-style draw-to-six calculation must draw 5. Reading only exchangeable hand counts predicts 6.

## Finding

Materialization can move a card out of an aggregate zone representation without moving the physical card out of that game zone.

Zone metrics such as hand size, deck size, discard size, or Lost Zone size should therefore be defined over the full identity ledger whenever materialized instances may inhabit that zone.

This is a representation invariant rather than a Crobat-specific rule.

## Relation to mandatory filler

The previously measured forced-search filler effect showed that omitting a mandatory fallback can overstate later draw-to-N volume by one.

This result identifies a second route to the same numerical error. The physical fallback or private target can exist correctly as a materialized hand instance while a later subsystem still loses it by reading only exchangeable counts.

The first error is transition semantics. The second is cross-layer projection.

## Validation

The regression checks the atomic Computer Search transaction, exact materialized X in hand, Crobat V hand-to-play materialization, physical hand counts before and after Crobat enters play, and the 5-versus-6 draw-to-six divergence.

## Next work

Use the physical zone-count projection inside continuation planners that read hand size. A broader unified-state invariant should require aggregate and materialized card layers to project to one canonical physical zone cardinality.
