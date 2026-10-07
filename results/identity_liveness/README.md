# Identity liveness and safe dematerialization

## Question

When can one exact physical card instance safely collapse back into an
exchangeable zone count?

The existing IdentityLedger already prevents dematerializing a card while it is
directly bound to a board object or attachment relation. The broader repository
now also has exact off-board identities whose liveness is owned by other layers:
a materialized deck top, a positioned Prize card, a private search target, or a
card still named by an enclosing effect.

That means off-board location alone is not a sufficient collapse condition.

Implementation: tools/identity_liveness.py
Regression: results/identity_liveness/reproduce.py

## Conservative rule

The new liveness gate requires both conditions:

1. the instance is in a caller-approved exchangeable zone;
2. no live higher-layer reference names that instance.

The default exchangeable zones are hand, unordered deck, discard, and Lost
Zone. The default deliberately excludes deck_top and prize because those
representations may still encode ordering, position, or observer-relative
information even though the card is off the board.

This is a sufficient safety rule. It is intentionally conservative. A
specialized subsystem may broaden the exchangeable-zone set after proving that
its additional relation has ended.

## Regression

One ledger contains five exact instances.

- x1 is an unreferenced hand card. The gate allows collapse.
- r1 is in hand but still named by an enclosing-effect reference. The gate
  blocks collapse until that reference is released.
- top-y is the exact materialized deck top. Its topology-sensitive zone blocks
  collapse.
- prize-a is an exact Prize instance. The default policy preserves it.
- energy-1 is attached to a Pokémon object. Both the attachment relation and
  the attached zone block collapse.

After x1 and then r1 become safe, dematerialization preserves both per-class
copy totals and canonical physical hand size. The representation changes while
the physical game state does not.

## Why this matters

Several repository results now depend on exact off-board identity.

- materialized hand cards contribute to physical hand size;
- a materialized deck-top card remains part of physical deck size;
- Prize-position and pending-Prize models use exact identities as information
  anchors;
- zone-exit transitions can deliberately preserve identity while an enclosing
  effect still refers to the moved card.

Without an explicit liveness boundary, one subsystem can erase an instance that
another subsystem still treats as a semantic key.

## Architectural consequence

Dematerialization should be treated as a representation transition with a proof
obligation. A useful default lifecycle is:

materialize -> preserve while referenced -> release references -> collapse

Zone movement does not by itself prove that identity has become exchangeable.

## Limits

The reference registry is explicit rather than automatically discovered. A
composite state owner still needs to collect the live instance references from
its participating subsystems.

The default Prize policy is conservative. Some states may safely collapse exact
Prize identity once position and observer-relative information have been
discarded, but that requires evidence from the owning Prize representation.

This result establishes the liveness seam. It does not yet provide a canonical
match object that owns every reference source.
