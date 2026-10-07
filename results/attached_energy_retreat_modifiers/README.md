# Board-derived attached-Energy Retreat modifiers

## Question

Which effectively legal Special Energy cards directly change their holder's
Retreat Cost, and can those effects be derived from the normalized physical
board?

## Surface

The current card pool contains three such exact prints:

- Magnetic Metal Energy `me4-85`: a Metal holder has no Retreat Cost;
- Hiding Darkness Energy `swsh3-175`: a Darkness holder has no Retreat Cost;
- Mystery Energy `xy4-112`: a Psychic holder's Retreat Cost is two Colorless
  less.

`tools/attached_energy_retreat_modifiers.py` encodes those exact print and
holder-tag predicates and emits the repository's existing
`RetreatCostModifier` representation.

## Normalization interaction

Mystery Energy is also holder-restricted. If its holder stops being Psychic,
the Energy's own card text discards it. The modifier therefore belongs
downstream of the attachment-validity normalization.

The regression demonstrates the ordering:

- on a Psychic holder, Mystery Energy changes base Retreat Cost 2 to zero and a
  free Retreat leaves the physical Energy attached;
- on a non-Psychic holder, the board-derived modifier is absent;
- the shared Energy normalizer discards that stale Mystery attachment;
- the holder still has Retreat Cost 2 and cannot Retreat for free.

Magnetic Metal and Hiding Darkness provide companion no-cost witnesses. Their
effects activate only on Metal and Darkness holders respectively.

## Strategic implication

Retreat Cost is derived board state.

A planner that stores only an already-resolved integer cost can become stale
when the holder changes type, an attached effect disappears, or an attachment
invalidates itself. Cost derivation should occur after current attachment
semantics have been normalized and before payment witnesses are enumerated.

## Scope

This result covers Special Energy sources only. The broader fixed-delta catalog
also contains Tools, Abilities, and attack-applied effects whose applicability
depends on source state, target state, duration, suppression, and ownership.
Those remain separate derivation layers.
