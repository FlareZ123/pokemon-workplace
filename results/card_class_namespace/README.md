# Namespaced card-class equivalence

## Question

What should `card_class` mean when exchangeable-copy state can be used by legality, gameplay, deck construction, and simulation subsystems?

It should be explicit about its equivalence relation.

Implementation: `tools/card_class_namespace.py`  
Regression: `results/card_class_namespace/reproduce.py`

## Why one unqualified class is unsafe

The repository now has several useful identities:

- exact database print ID;
- conservative gameplay fingerprint;
- eventual official functional-reprint equivalence;
- deck-building name;
- physical instance ID after materialization.

The reprint audit provides a direct reason to keep the middle two separate. Its official Copycat example has printings that the tournament rules treat as functionally equivalent even though the local conservative gameplay fingerprints differ.

The conservative fingerprint is therefore useful evidence and a research grouping. It is not the official reprint relation.

## Typed class keys

`CardClassKey` combines a namespace with a value. Current namespaces are:

- `exact_print`;
- `conservative_variant`;
- `official_reprint`;
- `deck_name`;
- `custom`.

The token form can be used as the existing string key in `ZoneCountState` without changing that state kernel.

The regression proves that the same raw value under four namespaces produces four distinct keys.

## Identity graph

The useful representation is better understood as a graph of relations than one universal identity ladder.

A physical card instance may have:

- one exact print provenance;
- one conservative local gameplay fingerprint;
- zero or one resolved official reprint class until authoritative equivalence is known;
- one deck-building name.

A persistent Pokémon board object can then own several physical Pokémon-card instances in an evolution stack. That board-object relation is many-to-one and changes over time, so it is not another card equivalence class.

## Modeling rule

Every exchangeable zone-count model should state which class namespace it uses.

A simulation that has already validated a deck may intentionally aggregate official functional reprints. A legality audit may need exact print IDs. A conservative experiment may prefer local gameplay variants. A copy-limit calculation may aggregate by deck-building name.

The key is to choose the relation explicitly rather than let a bare string silently change meaning between subsystems.

## Evidence

The computational counts and Copycat counterexample are maintained in `results/reprint_equivalence_candidates/` and `results/card_identity_resolution/`. This result contributes the state-modeling consequence rather than redefining tournament equivalence.
