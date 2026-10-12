# Mixed counters beat homogeneous techs in a restricted Shadow Rider / Iron Thorns opening

## Mechanically distinct ways around Initialization

The [Aichi champion Shadow Rider deck](../competitive_deck_baselines/) normally loses the Radiant Eternatus Climactic Gate line while opposing Active Iron Thorns ex suppresses Rule Box Abilities. Our [Cologne/Stone analysis](../shadow_rider_cologne_thorns_counter/) establishes a temporary answer using Canceling Cologne. An alternative is to **start Flutter Mane** (Temporal Forces sv5-78) Active: its non-Rule-Box **Midnight Fluttering** removes the opposing Active Thorns's Abilities, leaving the Radiant Eternatus's Ability available while Flutter occupies Active.

Flutter Mane is a Psychic, 90 HP, Basic Pokémon. Unlike Klefki, its printed effect targets only the *opponent's Active Pokémon*, so it does not disable the allied Radiant Eternatus Basic Pokémon. It offers a lasting control position while Active but occupies the one Active Spot and can be removed through opponent switching/gust or KO. Cologne is an Item whose Active-Ability negation lasts until turn end. Forest Seal Stone remains available to find one missing Cologne or Radiant through a Tool-printed VSTAR Power; it is already in the champion's 60.

The rules-derived comparison is conditional on opposing Iron Thorns ex starting Active and on absence of other suppression sources (Path to the Peak, Tool lock, Item lock, etc.). There is no opposing turn action between our first-turn actions. Flutter must appear **in the starting seven** to be chosen as starting Active; this model excludes later switching it Active using a Trainer or retreat. The player knows the opponent is Iron Thorns when choosing the modeled Active, an assumption appropriate to a known matchup or subsequent game in a match.

## Exact six-Prize first-turn comparison

Six conservative paper Expanded eligible exact-print 60-card lists are made from the [published champion baseline](../competitive_deck_baselines/shadow_rider_reproduce.py) by removing one Sky Field for each added card, up to the original two Sky Field copies. The counters are **Canceling Cologne** swsh10-136 and **Flutter Mane** sv5-78. All other published exact-print card quantities stay unchanged. The actual lists are constructed and adjudicated by [the reproducer](reproduce.py).

The exact model deals a Basic-accepted starting seven, physically allocates six unseen Prizes, and deals the going-second first turn's natural draw. The nine mutually exclusive physical card categories are Radiant Eternatus (1), Shadow Rider VMAX (4), Mysterious Treasure (4), Cologne (c), Flutter (f), Forest Seal Stone (1), Shadow Rider V (3), other opening Basics (10), and everything else (37-c-f).

Success requires two Shadow Rider VMAX still searchable in deck, plus one of these independent action families:

- Flutter already in the opening seven, selected Active, with Radiant in hand or retrievable by Treasure, or by Star Alchemy on a Shadow Rider V.
- Flutter absent from opening, another non-Radiant Basic opening Active, Cologne in hand (or fetched by Stone on a Shadow Rider V), and Radiant obtained directly, by Treasure, or by Stone's one use. A Stone can retrieve **one** missing card only.

Held Treasure is assumed to have a mechanically payable one-card discard; strategic cost is unpriced. Forest Seal Stone is assumed unused with an eligible Pokémon V and free Tool slot. No other search/draw, switch, opponent mulligan, manual attacks or Supporters are modeled.

| Techs replacing Sky Field | Exact restricted T1 counterline access |
| --- | ---: |
| No counter cards | 0.000000% |
| 1 Cologne | 6.820639% |
| 1 Flutter Mane | 5.886766% |
| 2 Cologne | 11.643271% |
| **1 Cologne + 1 Flutter Mane** | **11.981889%** |
| 2 Flutter Mane | 11.006152% |

**Ranking reversal:** Cologne is the stronger single-card addition for this access event. With two available slots, the mixed Cologne+Flutter package beats two Cologne by **0.338618 percentage points** and two Flutter by **0.975737 points**. The result follows from complementary turn-entry states and different access channels. It does **not** prove that the mixed package wins more actual matches. Both removal of Sky Field copies and active Flutter's cost can materially damage unrelated lines.

The basic-valid-opener conditioning is re-evaluated for each deck. Flutter increases the count of opening Basic Pokémon from 14 to 15 or 16, changing both mulligan rates and conditional composition. Compared probabilities are rates *among accepted openings*, which is the appropriate normalization for these particular game-state endpoint models.

## Full experimental 60-card mixed list (+1 Cologne +1 Flutter, −2 Sky Field)

These exact English print IDs describe an experimentally legal playable deck, preserving the original champion's remaining 58 physical cards.

| Qty | Card | Exact print |
| ---: | --- | --- |
| 3 | Shadow Rider Calyrex V | swsh6-74 |
| 4 | Shadow Rider Calyrex VMAX | swsh6-75 |
| 2 | Lillie's Clefairy ex | sv9-56 |
| 2 | Tapu Lele-GX | sm2-60 |
| 1 | Trevenant & Dusknoir-GX | smp-SM217 |
| 1 | Latias ex | sv8-76 |
| 1 | Dialga-GX | sm5-100 |
| 1 | Mimikyu | sm2-58 |
| 1 | Girafarig | sm8-94 |
| 1 | Marshadow | sm10-81 |
| 1 | Radiant Eternatus | swsh12pt5-105 |
| 1 | **Flutter Mane** | **sv5-78** |
| 2 | Lillie's Determination | me1-119 |
| 1 | Carmine | sv6-145 |
| 1 | Iono | sv2-185 |
| 1 | Teammates | xy5-141 |
| 1 | Raihan | swsh7-152 |
| 1 | Acerola | sm3-112 |
| 1 | Guzma | sm3-115 |
| 1 | Tulip | sv4-181 |
| 4 | Mysterious Treasure | sm6-113 |
| 4 | Fog Crystal | swsh6-140 |
| 3 | VS Seeker | xy6-110 |
| 1 | Quick Ball | swsh1-179 |
| 1 | Hisuian Heavy Ball | swsh10-146 |
| 1 | Battle Compressor Team Flare Gear | xy4-92 |
| 1 | Field Blower | sm2-125 |
| 1 | Night Stretcher | sv6pt5-61 |
| 1 | Unfair Stamp (ACE SPEC) | sv6-165 |
| 1 | Float Stone | xy8-137 |
| 1 | Forest Seal Stone | swsh12-156 |
| 1 | **Canceling Cologne** | **swsh10-136** |
| 1 | Dimension Valley | xy4-93 |
| 11 | Psychic Energy | bw1-109 |

**60 cards total: 19 Pokémon / 30 Trainers / 11 Energy; 15 Basics; one ACE SPEC; one Radiant.** This list is a hypothesis designed for follow-up tournament matchup testing, and no win-rate superiority is claimed.

## Validation and next work

[reproduce.py](reproduce.py) verifies Flutter's printed Midnight Fluttering, Iron Thorns Initialization, Radiant Climactic Gate, Cologne's Active suppression, Stone Star Alchemy, the six legal complete 60-card print constructions, exact rational fractions for each result, and a separate **21,840-world physical-label enumeration** against the nine-category weighted model. The associated Windows CI workflow executes the same checks.

The most promising next investigation is to price Flutter's forced Active status against actual early Energy/VMAX attacks, assess Cologne versus opposing Stadiums, and test the mixed package through complete two-player games. The numerical lead is small relative to strategic effects excluded from this setup metric.
