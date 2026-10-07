# Board-derived typed action permissions

## Question

The source-scoped restriction corpus contains legal effects that cannot be
represented faithfully by one scalar hand-action channel. Can the same canonical
board and causal lock state used for Trainer execution answer exact legality
questions for Pokémon plays, evolution, and Energy attachment?

Implementation: `tools/board_derived_action_permissions.py`

Regression: `results/board_derived_action_permissions/reproduce.py`

## Result

The evaluator derives all currently active continuous restrictions from the two
canonical boards and the resolved causal Ability-lock overlay, merges live
attack-applied temporal windows, projects the exact common subset into
`PlayerChannels`, and preserves residual typed predicates.

It returns the active restrictions, the hybrid projection, the exact restrictions
that block the attempted action, and the final legality decision. As an internal
consistency check, direct typed predicates and the channel-plus-residual result
must agree for each query.

## Regression witnesses

### Vileplume source sensitivity

Live Irritating Pollen blocks an Item played from hand. The same Item attempt
from `prize_pending` remains legal, preserving the Dream Ball-style source-zone
boundary.

### Team Rocket's Arbok selector and exception

Active Potent Glare blocks an ordinary Pokémon-with-Ability play from hand. An
otherwise identical Team Rocket's Pokémon remains legal because the printed
exception is preserved. A Pokémon without an Ability is also legal.

### Time Freeze target-scoped evolution

A live Dialga Time Freeze attack window blocks playing a Pokémon from hand to
evolve the Defending Pokémon. Evolution of another Pokémon remains legal, as
does playing a Basic Pokémon without using the evolution action mode.

### Cross Slicer target-scoped Energy

A live Palkia Cross Slicer window blocks Energy attached from hand to the
Defending Pokémon. Hand attachment to another Pokémon remains legal, and an
attachment sourced from the discard pile remains outside the printed hand
restriction.

## Finding

The canonical permission query can preserve source zone, action mode, card tags,
target relation, continuous Ability activation, causal Ability suppression, and
attack-effect lifetime in one boundary.

This is the semantic layer required before a simulator turns an abstract
"playable card" into a legal state transition. Compact channels remain valuable
as a verified acceleration path for the ordinary cases, while richer selectors
stay explicit.
