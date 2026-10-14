# Four-Block Snorlax Stall with two Tropical Beach

**Experimental paper Expanded 60.** [2026 Aichi third-place Japanese Snorlax Stall](https://limitlesstcg.com/tournaments/566/decklists), piloted by Haruto Miki, is the tournament source. This altered deck has no demonstrated tournament placement or match-winning rate.

## Construction and purpose

From the original Japanese deck, replace the Japanese-only Player's Ceremony with a second Tropical Beach, and replace one Plumeria with a fourth Snorlax. The **other 58 card copies** retain their published names and quantities.

This makes a different 60-card choice from the [one-card source adaptation with four Snorlax and one Beach](../snorlax-stall-4block-english/), which retains all four Plumeria, and from the [English third-place adaptation with three Snorlax and two Beach](../snorlax-stall-aichi-2026-english/). In this variant, the 4-Block attacker package has the original double Galarian Stunfisk count and the more redundant two-Beach draw plan, at the expense of a fourth Plumeria Energy-denial Supporter.

## Complete paper Expanded 60

### Pokémon (12)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Snorlax | `bw8-101` |
| 2 | Galarian Stunfisk | `swsh1-132` |
| 1 | Regirock | `xy7-40` |
| 1 | Mimikyu | `sv2-97` |
| 1 | Girafarig | `sm8-94` |
| 1 | Bunnelby | `xy5-121` |
| 1 | Articuno-GX | `sm7-31` |
| 1 | Rotom V | `swsh11-58` |

### Trainer (43)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 3 | Plumeria | `sm3-120` |
| 4 | Arven | `sv1-166` |
| 2 | Team Flare Grunt | `xy1-129` |
| 2 | Teammates | `xy5-141` |
| 2 | Lusamine | `sm4-96` |
| 1 | Team Rocket's Handiwork | `xy10-112` |
| 1 | Gladion | `sm4-95` |
| 1 | Guzma | `sm3-115` |
| 1 | Faba | `sm8-173` |
| 1 | Penny | `sv1-183` |
| 1 | Eri | `sv5-146` |
| 1 | Lillie's Determination | `me1-119` |
| 3 | Nest Ball | `sv1-181` |
| 3 | VS Seeker | `xy6-110` |
| 2 | Enhanced Hammer | `sv6-148` |
| 2 | Trainers' Mail | `xy6-92` |
| 2 | Counter Catcher | `sv4-160` |
| 1 | Scoop Up Cyclone | `sv6-162` |
| 1 | Quick Ball | `swsh1-179` |
| 1 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Night Stretcher | `sv6pt5-61` |
| 1 | Float Stone | `xy8-137` |
| 1 | Stealthy Hood | `sm10-186` |
| 1 | Tool Jammer | `swsh5-136` |
| 1 | Forest Seal Stone | `swsh12-156` |
| 2 | Tropical Beach | `bwp-BW28` |
| 1 | Temple of Sinnoh | `swsh10-155` |

### Energy (5)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 3 | Capture Energy | `swsh2-171` |
| 2 | Water Energy | `bw1-107` |

**Total: 12 Pokémon / 43 Trainers / 5 Energy = 60.** The sole ACE SPEC remains Scoop Up Cyclone. All 60 copies have traceable English print IDs.

## First-seven-card frontier

Probabilities are exact under uniform shuffle and the conditional event that the seven-card opening hand contains at least one Basic Pokémon.

| Resource-access event | 4 Snorlax / 1 Beach / 4 Plumeria | This list: 4 Snorlax / 2 Beach / 3 Plumeria |
| --- | ---: | ---: |
| Basic-valid opening (unconditional) | 80.93533% | 80.93533% |
| At least one Snorlax (conditional valid) | 49.36035% | 49.36035% |
| At least one Tropical Beach (conditional valid) | 10.97963% | **20.93189%** |
| At least one Plumeria (conditional valid) | **38.06444%** | 29.93547% |
| Both Snorlax and Tropical Beach (conditional valid) | 5.14042% | **9.82667%** |

A second Tropical Beach increases early access and reduces the event in which both copies are Prized from 10% for a singleton to 0.84746% for two. The cost is reduced natural access to Plumeria. Its discard-two cost, Supporter slot usage, VS Seeker recycling and the number of Energy-control turns needed must be considered before ranking this swap.

The fourth Snorlax increases immediate Block-start chance relative to the published three-Snorlax source. This same comparison can also raise mulligan resilience. These metrics do not establish that either English adaptation wins more games.

## Evidence and pending questions

The [independent reproducer](../../tests/snorlax_four_block_plumeria_trade/) compares exact opening probabilities and validates the changed 60 against the project's 12 October 2026 English-print paper Expanded eligibility snapshot. The [manifest](manifest.json) is machine-readable. The original historical top-three result belongs to the **Japanese source 60**, with Player's Ceremony and four Plumeria.

Snorlax's Block depends on keeping Snorlax Active. Practical counterplay varies by opponent: see the [Aichi Block escape-resource audit](../../tests/snorlax_block_escape_field/). A meaningful deck-level recommendation still requires tested ability suppression, switching effects, long-cycle Plumeria and Tropical Beach value, opponent Bench policy, Prize retrieval and deck-out scenarios.
