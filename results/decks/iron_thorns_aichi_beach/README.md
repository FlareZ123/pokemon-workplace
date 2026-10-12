# Iron Thorns ex: two-Tropical-Beach English-print alternative

**Status:** 60-card experimental paper Expanded deck, conservative English-print snapshot verified only after CI. An explicit one-slot tradeoff relative to the [two-DCE speed candidate](../iron_thorns_aichi_english/). Derived from Kazuma Kashi's sixth-place Aichi Open League 2026 Japanese list, [May 10 source](https://www.limitlesstcg.com/tournaments/566/decklists).

The source includes three Japanese-only entries. This English adaptation replaces Palace Book with one additional Trainers' Mail, Palace Belt with one additional Handheld Fan, and Player's Ceremony with a second Tropical Beach (BW28). The alternative has 4 Pokémon, 48 Trainers and 8 Energy.

## Full 60-card decklist

| Qty | Card | English print ID |
| ---: | --- | --- |
| **Pokémon** | | |
| 4 | Iron Thorns ex | sv6-77 |
| **Trainer** | | |
| 4 | Plumeria | sm3-120 |
| 3 | Guzma | sm3-115 |
| 2 | Guzma & Hala | sm12-193 |
| 2 | Team Flare Grunt | xy1-129 |
| 2 | Lusamine | sm4-96 |
| 1 | Cynthia & Caitlin | sm12-189 |
| 1 | Team Skull Grunt | sm1-133 |
| 1 | Faba | sm8-173 |
| 1 | Eri | sv5-146 |
| 1 | Sidney | swsh8-241 |
| 1 | Gladion | sm4-95 |
| 1 | Lillie's Determination | me1-119 |
| 1 | Team Rocket's Handiwork | xy10-112 |
| 4 | Crushing Hammer | sm1-115 |
| 4 | Trainers' Mail | xy6-92 |
| 3 | VS Seeker | xy6-110 |
| 2 | Tag Call | sm12-206 |
| 2 | Enhanced Hammer | sm2-124 |
| 2 | Camping Gear | swsh5-122 |
| 1 | Captivating Poké Puff | xy11-99 |
| 1 | Echoing Horn | swsh6-136 |
| 1 | Megaton Blower | sv8-182 |
| 2 | Handheld Fan | sv6-150 |
| 1 | Tool Jammer | swsh5-136 |
| 2 | Tropical Beach | bwp-BW28 |
| 1 | Thunder Mountain ◇ | sm8-191 |
| 1 | Wondrous Labyrinth ◇ | sm9-158 |
| **Energy** | | |
| 4 | Speed Lightning Energy | swsh2-173 |
| 2 | Capture Energy | swsh2-171 |
| 1 | Spiky Energy | sv9-159 |
| 1 | Double Colorless Energy | sm2-166 |

**Rules and evidence:** Four Iron Thorns ex are the only Basic Pokémon; Megaton Blower is the single ACE SPEC. Tropical Beach is a legal paper Expanded English promo according to the repository's conservative bundled October 12, 2026 print checker. The additional copy can be searched with Guzma & Hala when still in the deck. Once in play, Tropical Beach can end the player's turn by drawing until seven cards are in hand. It is symmetrical: the opponent can use it too.

[Manifest](manifest.json) contains exact print IDs, source provenance and all three substitutions. [SFT](reproduce.py) validates exact card-name/print identities, the 60-card composition, the one-slot relationship to the two-DCE candidate, and the bundled Expanded eligibility proof. Regional tournament legality is not separately certified.

## Matched two-option opening analysis

[Exact attack-versus-draw fallback model](frontier.md) compares the decks under identical Basic-valid 7-card opening, six hidden Prize cards, first going-second natural draw, and 12 *hypothetically acceptable* Guzma & Hala discard cards. The model gives priority to an available Thunder Mountain + DCE attack resource line. When that fails, it checks whether Tropical Beach is already held or searchable through G&H/Tag Call and can end the turn drawing up to seven. Other resource lines, Item/Tool value, opponents, and later turns are omitted.

| Fixed 60-card variant | Named attack package available | Failure with Tropical Beach fallback available |
| --- | ---: | ---: |
| Two DCE, one Tropical Beach | **20.953811%** | 27.046351% |
| One DCE, two Tropical Beach | 16.293836% | **39.657754%** |

Under a deliberately simplified utility U = 1 for attack-ready and U = v for fallback-ready, the second Beach becomes the better choice when the value of that fallback exceeds **0.369505** of the attack-ready event's value. This is a symbolic tradeoff threshold under the specified event model. It has no empirical basis as a real game's utility ratio.

**Priority next step:** model what the Beach draw actually retrieves and how the opponent benefits, using an explicitly defined two-turn continuation and matchup field. The current exact-access frontier is useful for determining which next research is worth doing; it cannot rank the decks competitively.

