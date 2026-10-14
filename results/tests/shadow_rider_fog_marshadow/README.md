# Fog Crystal repairs the Shadow Rider Marshadow access surface

## Mechanic and question

The published Aichi 2026 champion Shadow Rider Calyrex list contains **four Fog Crystal** (`swsh6-140`) and **one Marshadow** (`sm10-81`). Fog Crystal searches for a Basic Psychic Pokémon. Marshadow is a Basic Psychic Pokémon whose **Resetting Hole** Ability can discard Path to the Peak when Marshadow occupies the Bench, at the cost of discarding itself. Path and opposing Active Iron Thorns ex do not suppress Marshadow's non-Rule-Box Ability.

The previous [Marshadow correction](../shadow_rider_marshadow_path/) allowed Marshadow if already held, or if Forest Seal Stone retrieved it. It did not allow a held Fog Crystal to search the surviving Marshadow. This exact extension adds **only that missing connector branch**, preserving the original benchmark as a direct regression.

## Restricted model and assumptions

The full 60-card group inventory tracks Radiant Eternatus (1), VMAX (4), Mysterious Treasure (4), Cologne and Flutter tech additions (0–4 total), Forest Seal Stone (1), Shadow Rider V (3), other Basic Pokémon (9), Marshadow (1), Path answers (Field Blower plus remaining Stadiums), Basic Psychic Energy (11), Fog Crystal (4), and remaining cards. The counterfactual opponent board has an active Iron Thorns ex with Path to the Peak in play. There must be two Shadow Rider VMAX in deck for Radiant Eternatus's turn-ending Climactic Gate. Initial seven-card hands are conditioned on a legal Basic opener; the first going-second natural draw and all six hidden Prize cards are integrated exactly.

Energy-only policy permits **Mysterious Treasure to find Radiant Eternatus only with a Psychic Energy available for its mandatory discard**. Forest Seal Stone can supply a single missing launch role if a Shadow Rider V is held; a held Fog Crystal can additionally fetch Marshadow if it remains in deck. An opening Marshadow forced to Active cannot activate its Bench-only Ability. Resolving any Stadium answer, Cologne, and needed search occurs before benching Radiant, because Climactic Gate ends the turn.

As before, this is a **sufficient restricted launch-access endpoint**. The evaluator does not play the four Fog Crystals for any other purpose. In particular, it excludes Fog Crystal obtaining Shadow Rider V or Psychic Energy, Mysterious Treasure obtaining Marshadow, Quick Ball, sequential alternative tutors, subsequent draw actions, Bench crowding, realistic DCI resource sacrifices outside the Energy-only rule, opponent responses, damage, and match play. The four-tech variants have significant actual deck-cut opportunity costs.

## Exact results

Conditional first-turn access in the **Energy-only Treasure** policy:

| Cologne / Flutter added | Previous Marshadow model | With Fog Crystal to Marshadow | Gain (percentage points) |
| --- | ---: | ---: | ---: |
| 0 / 0 | 0.000000% | 0.000000% | 0.000000 |
| 1 / 0 | 1.876097% | 2.967210% | 1.091113 |
| 0 / 1 | 1.829778% | 2.873716% | 1.043938 |
| 2 / 0 | 2.606004% | 4.655582% | 2.049579 |
| **1 / 1** | **2.811878%** | **5.039163%** | **2.227285** |
| 0 / 2 | 2.750177% | 4.914216% | 2.164039 |
| 3 / 0 | 2.588795% | 5.650345% | 3.061551 |
| 2 / 1 | 2.748445% | 6.036099% | 3.287654 |
| 1 / 2 | 2.862631% | 6.310937% | 3.448306 |
| 0 / 3 | 2.809626% | 6.183379% | 3.373752 |
| 4 / 0 | 3.258063% | 7.083748% | 3.825684 |
| 3 / 1 | 3.410960% | 7.456445% | 4.045484 |
| 2 / 2 | 3.536759% | 7.762095% | 4.225336 |
| 1 / 3 | 3.624379% | 7.974356% | 4.349977 |
| 0 / 4 | 3.560201% | 7.821905% | 4.261705 |

For the two-tech one-Cologne/one-Flutter configuration, the revised **5.039163%** exceeds the earlier **2.811878%** by **2.227285 percentage points**, a **79.21% relative increase**. The restricted access-maximizing choice remains one Cologne plus the other allocated Flutter copies at tech counts one through four. That comparison prices no displaced cards and therefore does **not** establish that adding more tech cards improves the champion deck.

## Derivation and replication

The [self-contained reproducer](reproduce.py) uses exact integer combinatorial weights and `fractions.Fraction`. It enumerates accepted opening-seven compositions and the next natural draw. For Prizes, a 4-bit exhaustion mask for the Radiant, Cologne, Marshadow, and other Path-answer identities is computed by inclusion-exclusion; VMAX survival is checked independently with the two-required-in-deck condition. This compresses the Prize assignments without approximating physical-card probabilities.

The baseline fraction for **all 15** configurations is asserted equal to `EXPECTED_WITH_MARSHADOW_ENERGY_ONLY` from the previous study. Additional invariants assert 60-card conservation, weak dominance when enabling a genuinely optional Fog-to-Marshadow route, and the restricted winner by tech count. A **135,072-world fully labeled small-deck enumeration** separately reproduces the exact combinatorial result under all four policies. The source checks inspect the repository card JSON for Fog Crystal, Marshadow, Path, and Iron Thorns.

Run from the repository root with `python -m results.tests.shadow_rider_fog_marshadow.reproduce`. The Windows GitHub Actions workflow is **manual-dispatch only** to conserve shared CI.

## Next research

The most consequential remaining omitted connectors are Fog Crystal retrieving the V needed by Forest Seal Stone, and Mysterious Treasure retrieving Marshadow with an actual paid discard. Those uses compete for the same cards as Radiant Eternatus and later Psychic Energy acceleration. A sequence-aware model should choose legal connector uses jointly rather than count each route independently. Results must remain separated from full-game performance and actual tournament evidence.
