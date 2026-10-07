# Lock-gated manual Energy attachment

## Question

Can the normal once-per-turn Energy attachment consume target-aware lock legality
before it consumes the attachment quota?

Implementation: `tools/lock_gated_energy_attachment.py`

Regression: `results/lock_gated_energy_attachment/reproduce.py`

## Composition

The adapter verifies the selected physical hand copy against exact card-action
metadata, evaluates a hand-sourced `attach` attempt against canonical board
state, causal Ability suppression, ordinary temporal restrictions, and
Defending-Pokémon target bindings, then delegates to the existing
`energy_hand_attachment_events` owner.

A denied lock produces no attachment transition and therefore consumes no manual
attachment quota. If permission is legal but the generic turn quota has already
been spent, the permission remains legal while the mechanical attachment
transition returns no state. These are deliberately distinct failure modes.

## Regression witnesses

A Palkia Cross Slicer window bound to the original Defending Pokémon rejects a
Basic Energy attachment to that physical object without spending the manual
attachment quota. The same Energy can be attached to a different Pokémon, which
moves the physical hand copy into the attachment event state and consumes the
quota.

The same target-bound effect does not prohibit an attachment from another source
zone because its printed restriction is specifically Energy from hand.

## Finding

Action permission should be checked before action-budget consumption. Targeted
hand locks and generic once-per-turn quotas answer different questions and
should remain separate state owners.
