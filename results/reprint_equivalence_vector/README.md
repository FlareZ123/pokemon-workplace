# Reprint equivalence as a vector

## Question

Can a single gameplay fingerprint safely represent every reprint-equivalence question needed by paper Expanded research?

## Result

A vector representation is safer for the current evidence. Reprint comparison can involve physical state transitions, observer-relative information, target scope, timing, event semantics, and rule-category semantics. Tournament reprint policy is an additional status supported by official evidence.

This result adds `tools/reprint_equivalence_vector.py`, a small benchmark kernel that keeps those dimensions explicit.

## State-model axes

| Axis | Meaning |
| --- | --- |
| material transition | Reachable changes to cards, counters, attachments, and zones |
| private observation | Information learned by the acting player |
| public observation | Information revealed to all players or the opponent |
| target domain | Which game objects or players can legally be selected |
| timing | When the effect can occur and how often |
| event semantics | The rules identity of events such as damage versus placing damage counters |
| rule category | Card-type or rule-category meaning used by other effects |

Each axis can be `equivalent`, `divergent`, or `unmodeled`. The aggregate state-model status is divergent when any modeled axis diverges, unresolved when no axis diverges and at least one is unmodeled, and equivalent when every axis is equivalent.

Tournament status is tracked separately as `certified_equivalent`, `certified_non_equivalent`, or `unresolved`.

## Four benchmark pairs

| Pair | State-model status | Tournament status | Decisive evidence |
| --- | --- | --- | --- |
| Copycat `ex7-83` -> `sm7-127` | equivalent | certified equivalent | Current Tournament Handbook functional-reprint exemplar |
| Rainbow Energy `base5-17` -> `sm7-151` | divergent | certified non-equivalent | Damage and damage-counter placement are distinct mechanics |
| Life Herb `ex5-90` -> `sm7-136` | divergent | unresolved | Historical target exclusion has a reachable current Pokémon-ex witness |
| Pokédex `base1-87` -> `bw1-98` | divergent | unresolved | Physical deck-order outcomes agree while private observation can differ |

The Pokédex row is the main reason the vector is useful. The existing exact combinatorial result proves equality of physical top-deck outcomes for every available prefix size from one through five. The historical wording can expose fewer cards to the acting player, so private-information state can differ even when the final deck order is identical.

Life Herb shows a different kind of divergence. Its historical Pokémon-ex exclusion changes the legal target set in a state that current Expanded can realize. Rainbow Energy demonstrates an event-semantics distinction certified by official tournament guidance. Copycat supplies the positive control where current official guidance certifies functional equivalence.

## Relationship to the resolver

The vector complements `ReprintResolver`. It records why a pair agrees or diverges in a state model. The resolver records the current evidence ladder used for research legality decisions.

The regression cross-checks the benchmark profiles against the resolver:

- Copycat resolves as `official_semantic_candidate`.
- Rainbow Energy and Life Herb resolve as `known_non_equivalent`.
- Both older Pokédex printings remain `semantic_review`.

This separation prevents simulator semantics from silently becoming tournament-policy claims.

## Evidence classes

**Official rule and tournament evidence.** Copycat and Rainbow Energy come from the current Tournament Handbook examples already encoded by the repository. Current card text applies official errata before semantic comparison.

**Mathematical result.** The Pokédex physical-outcome equality is inherited from `results/pokedex_information_semantics/`.

**Current-format witness.** Life Herb's target-domain divergence is inherited from `results/reprint_divergence_predicates/`.

**Methodological result.** The four cases require at least three distinct semantic axes to explain their decisive differences: private observation, target domain, and event semantics.

## Reproduction

Run `python -m results.reprint_equivalence_vector.reproduce`.

The regression verifies all four profiles, recomputes the Pokédex physical/private-information distinction, and cross-checks every source print against the current reprint resolver.

## Limitations

The vector is a benchmark representation rather than a general natural-language card-text theorem prover. An `equivalent` label is used only where the repository has explicit evidence for that axis. `unmodeled` remains available when an axis has not been established.

Tournament status requires policy evidence. A state-model divergence can remain tournament-policy unresolved, as the Pokédex and Life Herb benchmarks demonstrate.

## Next work

Use the vector to classify additional high-value `semantic_review` families through small, rules-grounded semantic islands. Candidate families should be promoted only when the relevant axis can be proved or witnessed reproducibly.
