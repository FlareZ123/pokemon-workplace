# Correcting the Shadow Rider Path counter model: Marshadow Resetting Hole

## Previously omitted card

The published Aichi champion Shadow Rider Calyrex list already includes **one Marshadow (Unbroken Bonds sm10-81)**. Its non-Rule-Box Ability **Resetting Hole** can discard any Stadium while Marshadow is on the Bench, then discards Marshadow itself. Neither Path to the Peak's Rule Box restriction nor active Iron Thorns ex's Initialization turns off this non-Rule-Box Ability under the specified state. Consequently, Marshadow provides a third *kind* of Path answer alongside Field Blower and replacement Stadiums.

The parent [Path counter frontier](../../shadow_rider_path_counter_frontier/) modeled only the latter two kinds. Its probabilities remain exact for its explicitly restricted action set, but should **not be presented as exhaustive first-turn access in the actual champion list**.

## Corrected narrow model

This study splits Marshadow out of the original ten other Basic Pokémon. It can remove Path if drawn in the starting seven or natural first going-second draw **and** a different starting Basic can occupy the Active Spot. Forest Seal Stone can also search the single Marshadow from the remaining deck as its one missing-role search, provided it can be Benched. If Marshadow is the only usable non-Radiant starting Basic, it must start Active and Resetting Hole cannot be used. One Marshadow cannot be both Active and on the Bench. This corrects a positional oversight while conserving the original accepted-opening probability exactly.

The model continues to exclude **Mysterious Treasure or Fog Crystal searches for Marshadow**, Bench congestion, other draw/search, opposing later Stadiums, and gameplay after the opening line. It retains the earlier [Energy-only Treasure payment sensitivity](../shadow_rider_treasure_payment/) as one conservative sufficient-discard policy. The unrestricted Treasure case is computed for comparison. All 15 Cologne/Flutter decks and associated four-cut sequence are inherited from the [original full-deck legality study](../../shadow_rider_path_counter_frontier/).

## Exact conditional probabilities

| Cologne / Flutter added | Prior Energy-only model | With Marshadow Path answer | Improvement |
| --- | ---: | ---: | ---: |
| 1 / 0 | 1.498350% | 1.876097% | 0.377747 pp |
| 0 / 1 | 1.456201% | 1.829778% | 0.373577 pp |
| 2 / 0 | 1.895259% | 2.606004% | 0.710745 pp |
| **1 / 1** | **2.027751%** | **2.811878%** | **0.784127 pp** |
| 0 / 2 | 1.976244% | 2.750177% | 0.773933 pp |
| 3 / 0 | 1.498350% | 2.588795% | 1.090444 pp |
| 1 / 2 | 1.617348% | 2.862631% | 1.245284 pp |
| 1 / 3 | 2.046265% | 3.624379% | 1.578114 pp |

For the one-Cologne/one-Flutter pair, this additional card-text-valid route raises the conservative conditional first-turn launch endpoint by **0.784127 percentage points**, a **38.669793% relative increase** over the previously restricted model.

The corrected model also changes two structural conclusions of the earlier narrow analysis:

1. **One Cologne and three Cologne no longer have equal Path-present access.** Marshadow creates a new Path access channel whose availability is linked to the starting Active choice.
2. **The best three-slot restricted-access endpoint now exceeds the best two-slot endpoint.** The best two-slot package (1 Cologne / 1 Flutter) reaches 2.811878%; the best three-slot package (1 Cologne / 2 Flutter) reaches 2.862631%. The difference is 0.050753 percentage points. This is an access-only comparison that does not price the displaced Dimension Valley.

The best four-slot endpoint is 1 Cologne / 3 Flutter at 3.624379%, but those four counterfactual cuts retain their significant opportunity costs.

## Reproduce and interpretation

Run the module results.tests.shadow_rider_marshadow_path.reproduce from the repository root. It validates the source print sm10-81, benchmarks all 15 original unrestricted and Energy-only fractions, checks all 15 new exact restricted fractions, conserves 60-card probability mass, and matches an independently enumerated **68,936-world** labeled toy deal (opening, Prize, draw) in all four policies.

**Further exact extension:** [Fog Crystal-to-Marshadow access](../shadow_rider_fog_marshadow/) now includes the four existing Fog Crystal cards as a direct search route. The Energy-only one-Cologne/one-Flutter launch endpoint increases from 2.811878% here to **5.039163%** with that option. This page preserves the narrower historical benchmark for regression. Mysterious Treasure and other competing connector uses remain unmodeled, as do full-game consequences. These studies do not estimate match win rates or justify replacing tournament-tested Stadiums.
