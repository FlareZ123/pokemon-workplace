# Active source-scoped restriction aggregation

## Question

Multiple continuous and temporal restrictions can affect the same player simultaneously. This result combines those sources into one active restriction set before permission projection.

Implementation: `tools/active_source_scoped_restrictions.py`

Regression: `results/active_source_scoped_restrictions/reproduce.py`

## Composition

A continuous source carries its activation profile, current board context, source player, and opposing player. The aggregator evaluates its live geometry and printed target scope.

Attack windows already carry temporal state and source-relative scope. Only windows currently affecting the queried player contribute restrictions.

Duplicate restrictions are collapsed after activity is derived.

## Simultaneous witness

Player A controls a Benched Vileplume with Irritating Pollen. Player B has an Active Team Rocket's Arbok with Potent Glare and a live Psyduck Headache effect on A.

For A, the aggregate contains all three restrictions. The combined permission projection blocks an Item, a Supporter, and a Pokémon with an Ability while leaving an ordinary Pokémon play legal.

For B, only Irritating Pollen applies. Arbok does not target its owner and Headache targets A.

Disabling Arbok's Ability removes only that continuous source from A's aggregate.

## Finding

Active restriction state can be assembled immediately before an action from independently owned continuous and temporal sources. The resulting tuple is the canonical input to source-scoped permission projection and transaction gating.

This avoids persisting a single monolithic lock state that can become stale when one source moves, loses its Ability, expires, or changes scope.
