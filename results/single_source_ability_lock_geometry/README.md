# Single-source continuous Ability-lock geometry

## Question

Can continuous Ability suppression be evaluated from exact source identity, source position, target traits, target position, and Stealthy Hood protection without collapsing every lock into one global Ability boolean?

For one live source at a time, yes.

Implementation: `tools/single_source_ability_lock_geometry.py`  
Regression: `results/single_source_ability_lock_geometry/reproduce.py`

## Supported verified source families

The model checks every hard-coded print against the bundled card pool and effective Expanded legality.

It currently includes:

- Wobbuffet / Bide Barricade: Active, both players, Psychic targets exempt;
- Galarian Weezing / Neutralizing Gas: Active, opponent only;
- Slaking / Lazy: Active, opponent only;
- Gastrodon / Sticky Bind: Bench, both players, only Benched Stage 2 targets;
- Garbodor / Garbotoxin: Tool-attached, both players, Garbotoxin exempt.

The profiles preserve exact print families rather than matching only by card name.

## Geometry matters to Dual Brains

Magnezone `bw8-46` is represented as a Stage 2 Metal Pokémon. The regression shows that the same physical Dual Brains source can be live or suppressed solely because geometry changes:

- active opposing Wobbuffet suppresses it;
- the same Wobbuffet profile does not suppress a Psychic-tagged target;
- opposing Galarian Weezing suppresses it only while Weezing is Active;
- opposing Slaking suppresses it while Active, while the owner's own Slaking does not because Lazy is opponent-scoped;
- Benched Gastrodon suppresses Dual Brains when Magnezone is also a Benched Stage 2, while moving Magnezone Active removes that target match.

The resulting suppressed-object IDs can feed directly into `derive_board_action_quotas(...)`.

## Protection

For opponent-sourced Ability effects, live Stealthy Hood removes the target from the suppression overlay. Jamming Tower makes the Hood's effect unavailable and puts the target back into the overlay.

Same-side effects are not blocked by Hood.

## Why single-source only

Continuous Ability locks can suppress other continuous Ability-lock sources. A pair such as two opposing source families can therefore create a dependency problem that cannot be solved safely by independently unioning every source profile.

This result intentionally avoids inventing a fixed-point rule or timestamp rule for that unresolved case. It establishes the target/geometry predicate layer that a future dependency resolver can use.

## Architectural implication

Ability activity should be derived from at least:

`source identity + source geometry + target scope + target traits + target geometry + protection state`

A single global `abilities_allowed` flag aliases these states. The same Magnezone can lose or regain Dual Brains through movement alone, even with every card identity unchanged.
