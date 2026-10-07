# Holder-restricted Special Energy revalidation

## Question

Can an attached Special Energy become an illegal attachment after its holder
changes, and can that stale physical state create an illegal Retreat branch?

## Card-pool surface

A reproducible scan of effectively legal paper Expanded Special Energy finds
**24 print rows across 19 distinct names** whose text both restricts what kind
of Pokemon they may be attached to and instructs the player to discard the card
if it is attached to anything else.

The represented requirements span:

- Pokemon types from Grass through Dragon;
- Battle Styles: Rapid Strike, Single Strike, and Fusion Strike;
- Team Aqua, Team Magma, and Team Rocket's Pokemon;
- Evolution Pokemon for Triple Acceleration Energy.

`tools/restricted_special_energy_catalog.py` parses this surface directly from
the repository card database. The regression requires the catalog to equal the
runtime exact-print registry, so a future card-pool change cannot silently leave
new restricted prints unmodeled.

## Conserved post-mutation normalization

`tools/restricted_special_energy_attachment.py` takes an
`EnergyBoardState` after a holder mutation and checks each materialized Energy
attachment against its exact-print rule.

When a holder no longer satisfies the restriction:

1. the physical Energy instance is removed from that holder;
2. its card-class count moves from `attached` to `discard`;
3. its materialized attachment index entry is removed;
4. all other board objects and Energy copies remain unchanged.

Unknown prints and name/print mismatches are preserved rather than receiving a
guessed restriction.

## Triple Acceleration Retreat counterexample

The regression begins with Triple Acceleration Energy `sm10-190` legally
attached to a Stage 1 Pokemon and represented as three Energy units. It then
models a completed holder mutation to a Basic Pokemon while preserving the
physical attachment.

Without revalidation, the raw Retreat transaction can consume the stale
three-unit card to pay Retreat Cost 3. That continuation should not exist
because Triple Acceleration Energy says it must be discarded when attached to
anything other than an Evolution Pokemon.

After revalidation, the physical card is already in discard and the same
Retreat payment is impossible.

Double Dragon Energy `xy6-97` supplies the type-based companion witness: it
survives on a Dragon holder and is discarded after the holder becomes
non-Dragon.

## Strategic implication

Physical attachment conservation needs a semantic normalization boundary after
holder-changing transitions.

The safe order is:

1. apply the holder mutation while preserving attached card identity;
2. revalidate attachment restrictions;
3. refresh state-dependent Energy provision;
4. enumerate later actions such as Retreat.

Skipping step 2 can turn an attachment that should self-discard into spendable
Energy and can therefore create false tactical lines.

## Scope

This result handles the immediate holder-restriction discard clause. Separate
timed clauses such as Triple Acceleration Energy's end-of-turn discard and
Double Aqua/Double Magma Energy's end-of-turn discard remain outside this
normalizer.

The holder-tag vocabulary is explicit. Future work can derive those tags from
Pokemon print metadata or a stronger typed board identity layer.
