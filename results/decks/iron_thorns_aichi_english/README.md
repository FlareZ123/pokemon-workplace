# Iron Thorns ex: Aichi sixth-place English-print adaptation

**Status:** 60-card experimental paper Expanded deck candidate. It preserves 57 card copies by name and quantity from Kazuma Kashi's May 10, 2026 Aichi sixth-place Japanese list, [published by Limitless](https://www.limitlesstcg.com/tournaments/566/decklists). Three Japanese-only cards have been replaced to provide exact English physical prints. Competitive match strength remains unmeasured.

## Three controlled replacements

| Japanese-only original | English adaptation | Strategic opportunity cost |
| --- | --- | --- |
| Palace Book (Japanese-only) | Trainers' Mail | Adds one more Item-based Supporter search opportunity; Palace Book's end-turn draw-three is lost. |
| Palace Belt (Japanese-only) | Handheld Fan | Adds an energy-disruption Tool; Palace Belt's extra natural card draw is lost. |
| Player's Ceremony (Japanese-only) | Double Colorless Energy | Improves the attack-cost package searchable with Guzma & Hala; the end-turn draw-two Stadium option is lost. |

**Research status:** The replacement effects are different. Their full turn-level consequences require further testing. The double Colorless variant prioritizes an opening Volt Cyclone resource package. No optimized-deck ranking is claimed.

## Fully specified 60-card list

| Qty | Card name | English print ID |
| ---: | --- | --- |
| **Pokémon** | | |
| 4 | Iron Thorns ex | `sv6-77` |
| **Trainer** | | |
| 4 | Plumeria | `sm3-120` |
| 3 | Guzma | `sm3-115` |
| 2 | Guzma & Hala | `sm12-193` |
| 2 | Team Flare Grunt | `xy1-129` |
| 2 | Lusamine | `sm4-96` |
| 1 | Cynthia & Caitlin | `sm12-189` |
| 1 | Team Skull Grunt | `sm1-133` |
| 1 | Faba | `sm8-173` |
| 1 | Eri | `sv5-146` |
| 1 | Sidney | `swsh8-241` |
| 1 | Gladion | `sm4-95` |
| 1 | Lillie's Determination | `me1-119` |
| 1 | Team Rocket's Handiwork | `xy10-112` |
| 4 | Crushing Hammer | `sm1-115` |
| 4 | Trainers' Mail | `xy6-92` |
| 3 | VS Seeker | `xy6-110` |
| 2 | Tag Call | `sm12-206` |
| 2 | Enhanced Hammer | `sm2-124` |
| 2 | Camping Gear | `swsh5-122` |
| 1 | Captivating Poké Puff | `xy11-99` |
| 1 | Echoing Horn | `swsh6-136` |
| 1 | Megaton Blower | `sv8-182` |
| 2 | Handheld Fan | `sv6-150` |
| 1 | Tool Jammer | `swsh5-136` |
| 1 | Tropical Beach | `bwp-BW28` |
| 1 | Thunder Mountain ◇ | `sm8-191` |
| 1 | Wondrous Labyrinth ◇ | `sm9-158` |
| **Energy** | | |
| 4 | Speed Lightning Energy | `swsh2-173` |
| 2 | Capture Energy | `swsh2-171` |
| 1 | Spiky Energy | `sv9-159` |
| 2 | Double Colorless Energy | `sm2-166` |

**Deck totals:** 4 Pokémon / 47 Trainers / 9 Energy. Four starting Basic Pokémon, all Iron Thorns ex. Megaton Blower is the sole ACE SPEC. Thunder Mountain ◇ and Wondrous Labyrinth ◇ are distinct Prism Star Stadiums.

## Exact named-resource access comparison

The existing [Iron Thorns Guzma & Hala access model](../../iron_thorns_gnh_side_payload/) conditions on a valid seven-card opener containing Iron Thorns, sets six hidden Prize cards, and includes one natural draw going second. Card-group counts held constant between comparison lists are Iron Thorns 4, Tag Call 2, Guzma & Hala 2, Thunder Mountain 1, and three modeled Tools. A second Double Colorless Energy displaces one filler card.

| DCE copies | Idealized access to Mountain + DCE package |
| ---: | ---: |
| 1 (source list) | 33.781505711% |
| 2 (adaptation) | 38.080679951% |

**Increase: +4.299174240 percentage points** for the model's named resource-access endpoint. The access classes are (1) held Mountain plus held DCE, (2) G&H or Tag Call to G&H reaching necessary deck resources without Special Energy discard payment, or (3) an analogous G&H branch whose Special Energy access requires a two-card discard.

The model classifies the discard branch but does not require two strategically disposable cards or optimize alternative uses of a Supporter. It also excludes locks, Stadium competition, attack restrictions, the benefit of the removed draw Stadium, and opponent actions. Therefore this percentage is an idealized access envelope; a played first-turn attack rate and game win rate have yet to be measured.

## Validation and next research

[Reproducer](reproduce.py) checks exact print names, quantities, construction, a conservative bundled Expanded snapshot as of October 12, 2026, and the fixed-size resource-access counterfactual. [Manifest](manifest.json) holds 32 card identities and source attribution. [Windows CI workflow](../../../.github/workflows/validate-iron-thorns-aichi-english.yml) runs the regression. Official regional tournament eligibility still requires independent adjudication.

Useful next tests include a same-size 1-DCE adaptation retaining an end-turn draw Stadium, exact Guzma & Hala discard payability, alternative Supporter contention, and matchup outcomes against the published Shadow Rider, Vileplume, Regidrago, and Mew baselines.

