# Exact topology can publish identity-liveness references

## Question

The identity-liveness gate accepts caller-supplied references. Can the existing
exact deck and Prize state objects publish those references mechanically instead
of requiring each caller to reconstruct them?

Yes.

Implementation: tools/identity_reference_sources.py
Regression: results/identity_reference_sources/reproduce.py

## Reference adapters

top_prize_identity_references derives one reference for:

- the exact deck-top instance;
- every exact Prize-position instance.

pending_prize_identity_references adds one reference for every exact pending
Prize queue entry.

These references describe representation ownership. They do not change card
zones or beliefs.

## Stronger regression

The liveness gate already blocks deck_top and prize under its conservative
default exchangeable-zone policy.

The regression intentionally broadens the caller-approved zone set to include
deck_top, prize, and prize_pending. This removes the zone blocker and asks
whether topology ownership alone is sufficient to preserve identity.

It is.

- top-1 is blocked by reference:deck_top;
- prize-a is blocked by reference:prize_slot:0;
- after prize-b is staged out of its slot, it is blocked by
  reference:prize_pending:0.

This demonstrates that identity lifetime can remain safe even when zone policy
and topology policy are separated.

## Architectural consequence

A composite state can collect liveness claims from each subsystem that owns
exact physical identity.

The emerging split is:

- IdentityLedger owns the physical instance;
- topology state owns exact positional relations;
- belief state owns observer-relative uncertainty;
- pending-effect state owns temporary semantic references;
- the liveness gate decides whether all such ownership has ended.

This is a path toward automatic reference collection without making
IdentityLedger aware of every higher-level representation.

## Limits

The adapters cover TopPrizePhysicalState and PrizePendingTakeState only.
Observer-relative belief objects may retain latent identity relationships that
need their own reference adapters when their state keys are physical instance
IDs.

Board relations are already protected directly by attached_to and
board_object_id, so this result does not add duplicate board-reference rows.
