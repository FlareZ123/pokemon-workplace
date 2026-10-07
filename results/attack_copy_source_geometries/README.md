# Remaining attack-copy source geometries

## Question

Can the small executable copy kernel represent the source and chooser semantics that were previously absent from the 30-signature static catalog?

The remaining high-level geometries now have explicit representations.

Implementation: `tools/attack_copy_kernel.py`  
Regression: `results/attack_copy_source_geometries/reproduce.py`

## Previous-Evolution copying

Three catalog signatures use attacks from the copying Pokémon's previous Evolutions: two **Recall** wordings and **Secret Attack**.

The kernel now lets the active physical Pokémon carry `previous_evolution_attacks`. A `self_previous_evolution` selector reads that actor-specific history.

This keeps the source tied to the current evolved object rather than treating previous Evolutions as an arbitrary external zone.

## Opponent-owned selection

**Mimed Games** is structurally different from ordinary copy attacks because the opponent chooses the attack from one of their Pokémon in play.

The kernel now records selector choice authority as either `actor` or `opponent`.

An opponent-owned selector requires a separate opponent choice policy. If none is supplied, resolution raises `MissingCopyChooser` instead of silently letting the attacking player choose.

The regression supplies different actor and opponent policies and confirms that only the opponent policy determines the selected body.

## Named Bench families

**Night Joker** can use attacks from the user's Benched N's Pokémon.

The kernel now supports an exact name-prefix predicate on card-backed sources. The regression places both `N's Reshiram` and ordinary `Reshiram` on the Bench and confirms that only the named-family source contributes a candidate.

## Architectural implication

Choice authority and source provenance are separate state dimensions.

Two copy attacks can share the same broad geometric source, such as the opponent's in-play Pokémon, while differing in who controls target selection. Likewise, a Bench source can have a semantic family filter that cannot be recovered from the zone alone.

The copy contract therefore needs to preserve:

`zone geometry + card predicates + chooser + physical source identity`

before nested execution begins.

## Limitations

The previous-Evolution representation stores the attacks available from the actor's evolution history rather than materializing the full evolution stack. A future integration with the repository's board-stack model should derive this field from the canonical in-play stack.

The name-prefix predicate covers the current N's Pokémon wording. More general named-family rules may need a typed tag system rather than string matching.
