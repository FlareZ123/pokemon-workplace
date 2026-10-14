# Four-Block Snorlax Stall: alternative English paper Expanded 60

**Status:** Experimental English-print adaptation of Haruto Miki's [third-place 2026 Aichi Open League Snorlax Stall](https://limitlesstcg.com/tournaments/566/decklists). Tournament place applies to the Japanese source 60. This altered English list is **untested in matches**.

## One-card transformation from the Japanese source

The source list's single Japanese-only **Player's Ceremony** is replaced by one additional **Snorlax `bw8-101`**. All other 59 source copies and their card-name quantities are preserved, including two Galarian Stunfisk and the source's one Tropical Beach.

This differs from the repo's [original English adaptation](../snorlax-stall-aichi-2026-english/), which substitutes a **second Tropical Beach** for Player's Ceremony. Both are English-print legal under the 12 October 2026 project snapshot. The additional Snorlax is another Basic starter with Block, whereas the additional Tropical Beach increases draw-Stadium availability.

## Complete 60-card list

### Pokémon (12)

| Copies | Card | Verified English print |
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

| Copies | Card | Verified English print |
| ---: | --- | --- |
| 4 | Plumeria | `sm3-120` |
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
| 1 | Tropical Beach | `bwp-BW28` |
| 1 | Temple of Sinnoh | `swsh10-155` |

### Energy (5)

| Copies | Card | Verified English print |
| ---: | --- | --- |
| 3 | Capture Energy | `swsh2-171` |
| 2 | Water Energy | `bw1-107` |

**Total: 12 Pokémon + 43 Trainers + 5 Energy = 60.** One Scoop Up Cyclone ACE SPEC. The manifest contains exact set print IDs.

## Exact first-seven-card frontier

Condition on a valid opening seven containing at least one Basic Pokémon. A player who sees a Snorlax in their opening hand can legally choose it as the starting Active, making Block available when play begins. These numbers count initial seven-card access and legal Basic selection. They do not count later attacks, supporting Item and Supporter searches, switching, or game wins.

| Exact event | 3 Snorlax / 2 Beach baseline | 4 Snorlax / 1 Beach proposal |
| --- | ---: | ---: |
| Unconditional seven-card Basic validity | 77.75789% | **80.93533%** |
| At least one Snorlax, given Basic-valid | 40.56561% | **49.36035%** |
| At least one Tropical Beach, given Basic-valid | **20.81999%** | 10.97963% |
| Both Snorlax and Tropical Beach, given Basic-valid | **8.01672%** | 5.14042% |

The fourth Snorlax increases conditional immediate Block-start access by **8.79474 percentage points** and opening Basic validity by **3.17744 points**. Removing a Tropical Beach reduces the conditional Beach-in-opening chance by **9.84036 points**. Availability of at least one Beach throughout the game can also suffer: when no copies have been drawn, a singleton has a 10% unconditional chance to be among the six initial Prize cards, whereas both copies being Prized has a probability of 0.84746% when the deck has two.

A different 4-Snorlax allocation removing one of the two Galarian Stunfisk would preserve both Tropical Beach and yield 51.37738% conditional Snorlax opening access, but would reduce Snap Trap backup redundancy. A remaining singleton Stunfisk is initially Prized 10% of the time, versus 0.84746% for both copies being Prized when the deck includes two. Hisuian Heavy Ball and Gladion provide potential Prize-recovery lines that these isolated probabilities do not model.

## Interpretation and evidence

**This is a setup/reliability tradeoff.** The source is a stall deck with long control games; losing a search-independent turn-ending draw Stadium may cost substantially more than these opening statistics show. The extra Block attacker improves the ability to establish a Snorlax Active, and the initial mulligan pressure decreases. A real head-to-head comparison would need capable opponent policies and precise Tropical Beach action sequencing, gust, switching, Ability lock and deck-out handling.

Evidence and reproduction: [source adaptation](../snorlax-stall-aichi-2026-english/), [exact combinatorics and print checks](../../tests/snorlax_starter_draw_frontier/), plus original [Aichi tournament record](https://limitlesstcg.com/tournaments/566/decklists). [Manifest](manifest.json) provides the complete source-derived candidate with print IDs. Deck construction is checked against the repository's October 12, 2026 English paper Expanded eligibility snapshot; later event-specific eligibility is a separate question.
