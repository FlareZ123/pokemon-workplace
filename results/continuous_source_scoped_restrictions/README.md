# Continuous source-scoped restriction evaluator

## Question

The activation compiler classifies 29 direct hand restrictions as continuous Pokémon Abilities. This result turns those profiles into an executable board-context predicate while leaving causal Ability suppression under the existing Ability-lock state owner.

Implementation: `tools/continuous_source_scoped_restrictions.py`

Regression: `results/continuous_source_scoped_restrictions/reproduce.py`

## Context contract

A `ContinuousRestrictionContext` supplies only the state needed by this semantic island:

- whether the source Pokémon is still in play;
- whether its Ability is currently effective;
- whether the source is Active;
- whether the source has the required Tool;
- whether a Stadium is in play;
- each player's Pokémon count when a relative-count condition is present.

The evaluator accepts only continuous activation profiles. Passing an attack-applied restriction raises instead of silently applying board-state logic to a temporal effect.

## Global invariants

The regression evaluates all 29 continuous profiles against two invalidating contexts.

If the source is absent, every profile is inactive.

If the source remains in play while its Ability is disabled, every profile is inactive.

This makes the interface compatible with the repository's causal Ability-lock work: that subsystem can decide whether an Ability is effective, then this evaluator applies the source's remaining board geometry.

## Geometry witnesses

Vileplume `xy7-3` / Irritating Pollen remains active from the Bench because its activation family is general in-play.

Team Rocket's Arbok `sv10-113` / Potent Glare is inactive on the Bench and active in the Active Spot.

Genesect `sv6pt5-40` / ACE Nullifier requires a Pokémon Tool attached to its source.

Barbaracle `xy10-23` / Hand Block requires a Stadium in play.

Omastar `sm9-76` / Fossil Bind is active when its player has fewer Pokémon in play than the opponent and becomes inactive at equal counts.

## Finding

Continuous restriction activity can be derived as a pure projection of effective Ability state plus local board geometry.

This keeps three ownership boundaries clear:

- causal Ability-lock kernels decide whether an Ability exists and functions;
- the continuous restriction evaluator decides whether the printed board condition is satisfied;
- source-scoped permission predicates decide whether the resulting active restriction blocks the attempted card action.

The layers can therefore be recomputed independently after board movement, Tool changes, Stadium changes, Knock Outs, or Ability-suppression changes.

## Limits

The context is intentionally compact and supports the 29 audited direct restrictions. It does not infer source objects from a full board state.

A later board adapter can construct the context from canonical Pokémon objects, attachment state, Stadium state, and the effective suppression overlay.

Attack-applied restrictions remain outside this evaluator and need a temporal owner with explicit application and expiration events.
