# Colorless attack-cost extension: resource typing and payment semantics

The earlier [three-colored-cost theorem](README.md) deliberately excluded Colorless. This extension checks the remaining costs and makes a reusable semantic distinction explicit.

## Distinct meanings of Colorless

A **Colorless attack-cost symbol** accepts an Energy unit of any type. An attack that costs Grass/Colorless can be powered by Basic Grass and Basic Fire Energy, for example. This is reflected in the repository's `energy_action_budget.py` via `_unit_matches`, where a Colorless attack-cost symbol returns true for every unit.

Conversely, an instruction such as `discard a Colorless Energy` refers to the type currently provided by an Energy card. For that latter purpose, the existing `energy_discard_solver.max_typed_match` intentionally uses strict type matching. Replacing all strict matches with attack-cost wildcard matching would incorrectly expand the meaning of typed discard instructions.

The extension adds an **attack-cost-specific wrapper** that includes Colorless in the accepted symbols of each provider unit while delegating subset assignment to the repository's strict matching solver.

## Bounded exhaustive result

The setup remains one active Double Dragon Energy plus three Basic Energy cards (drawn as type-composition multisets from nine Basic types). An earlier copied attack requires discarding two generic Energy units. We consider every multiset of three next-attack cost symbols drawn from the nine colors plus Colorless, with exactly the same attack-copy/retained-attachment assumptions as the earlier theorem.

| Colorless cost symbols | Cost multiset signatures | Initially Energy-ready pairs | One-card DDE discard preserves | One-card DDE discard loses, two-Basic discard preserves |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 165 | 15,393 | 165 | 15,228 |
| 1 | 45 | 7,425 | 405 | 7,020 |
| 2 | 9 | 1,485 | 405 | 1,080 |
| 3 | 1 | 165 | 165 | 0 |
| **Total** | **220** | **24,468** | **1,140** | **23,328** |

Across all **36,300** cost/attachment-composition pairs, the existing full provider state is Energy-ready in 24,468. Each of those can retain the next attack's exact cost by discarding two Basics. In 23,328 cases, the minimum physical-card payment (discard DDE) loses that cost's readiness.

The cases with Colorless differ sharply. A three-Colorless next-attack cost remains feasible after discarding DDE because any three Basic Energy cards can pay three generic Colorless symbols. With one Colorless and two colored cost symbols, all 165 Basic type mixtures are initially ready, but only nine preserve the next attack after DDE alone is discarded.

`tools/energy_discard_colorless_cost_extension.py` runs all 36,300 cases, checks that a two-Basic preservation option exists exactly whenever the starting Energy can pay the next attack, and asserts the aggregates. The abstract predicate was independently cross-checked with a separate slot-level backtracking oracle locally.

Run `python -m tools.energy_discard_colorless_cost_extension` from the repository root.

## Boundaries

The theorem is about generic two-unit discard cost followed by one potential three-unit attack. Printed card text may create other constraints or strategic reasons to prefer the one-card payment. The model treats DDE's Energy provision as active and assumes the Pokémon remains in play. Percentages over these artificial type-signature and Basic-mixture populations are not gameplay frequencies.

The key simulator-design lesson is to keep Energy-*type* matching for a card effect separate from generic Colorless-*cost* payment.
