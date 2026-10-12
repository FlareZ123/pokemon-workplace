# Mew VMAX / Genesect V | experimental Sky Field 3, Path to the Peak 1

**Status:** Complete 60-card paper Expanded-eligible counterfactual to
Yamato Nakano's May 10, 2026 Aichi Open League fifth-place
[Mew/Genesect tournament list](../mew-genesect/).
Every exact English print is identified below and in the
[machine-readable manifest](deck.json). The baseline print selection and the
one-card counterfactual pass the project's 2026-10-12 Expanded snapshot
adjudicator. Representative English print IDs need not match the original
Japanese tournament artwork.

The only change to the published list is **+1 Sky Field (xy6-89), −1 Path to
the Peak (swsh6-148)**. This changes which Stadium is available when an
opponent's Path suppresses Genesect's Fusion Strike System. The swap loses
one copy of our own potential Path disruption and has no demonstrated
improvement in full-game match win rate.

## Complete 60-card list

### Pokémon (14)

| Qty | Card | Exact English print |
| ---: | --- | --- |
| 4 | Mew V (Fusion Strike) | swsh8-113 |
| 3 | Mew VMAX | swsh8-114 |
| 4 | Genesect V | swsh8-185 |
| 1 | Dedenne-GX | sm10-57 |
| 1 | Crobat V | swsh3-104 |
| 1 | Lillie's Clefairy ex | sv9-56 |

### Trainers (42)

| Qty | Card | Exact English print |
| ---: | --- | --- |
| 2 | Guzma | sm3-115 |
| 2 | Karen | xyp-XY177 |
| 1 | Wally | xy6-94 |
| 1 | Marnie | swsh1-169 |
| 1 | Pokémon Ranger | xy11-104 |
| 4 | Quick Ball | swsh1-179 |
| 4 | Ultra Ball | swsh9-150 |
| 3 | Trainers' Mail | xy6-92 |
| 3 | Battle VIP Pass | swsh8-225 |
| 2 | Special Charge | xy11-105 |
| 2 | VS Seeker | xy6-110 |
| 2 | Special Red Card | me4-82 |
| 1 | Enhanced Hammer | sv6-148 |
| 1 | Field Blower | sm2-125 |
| 1 | Lost Vacuum | swsh11-162 |
| 1 | Escape Rope | swsh5-125 |
| 1 | Hisuian Heavy Ball | swsh10-146 |
| 1 | Secret Box (ACE SPEC) | sv6-163 |
| 2 | Muscle Band | xy1-121 |
| 2 | Float Stone | xy8-137 |
| 1 | Forest Seal Stone | swsh12-156 |
| 3 | Sky Field | xy6-89 |
| 1 | Path to the Peak | swsh6-148 |

### Energy (4)

| Qty | Card | Exact English print |
| ---: | --- | --- |
| 4 | Double Colorless Energy | sm1-136 |

**Totals: 60 cards, 14 Pokémon, 42 Trainers, four Energy; eleven starting
Basic Pokémon, one ACE SPEC.**

## Exact source-access result

The [reproducible Prize-aware study](../../tests/mew_genesect_path_escape/)
compares a valid seven-card opening, six Prizes, and the first natural draw.
It requires that an opponent's Path is already in play and allows every
naturally held Trainers' Mail to inspect four cards from the remaining deck.
Its objective is access to Sky Field or Field Blower, optionally including
Lost Vacuum under an assumed available discard payment.

| Early Path counter-access source metric | Tournament Path2 / Sky2 | Proposed Path1 / Sky3 |
| --- | ---: | ---: |
| Excluding Lost Vacuum | 39.356522079% | **48.918875822%** |
| Assuming Lost Vacuum payable | 48.918875822% | **57.087568204%** |
| Given a naturally visible Genesect V, excluding Vacuum | 37.954301459% | **47.315832734%** |
| Given a naturally visible Genesect V, assuming Vacuum payable | 47.315832734% | **55.373523050%** |

The reported improvement is a **restricted source-access probability**.
Full Genesect draws, Search Items other than Trainers' Mail, Secret Box,
Supporter sequencing, Item lock, and actual field-wide match outcomes are
outside this specific test.

Four independent exact labeled-card toy-world oracles and both full
60-card snapshot constructions passed
[CI 38293107728](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293107728).
The current source is exercised again after its migration into results/tests.

## Play and matchup cautions

Path to the Peak is also an offensive disruption card. Its singleton copy
may be less likely to stop an opponent's Rule Box Abilities late in a game.
Sky Field supports larger Benches for both players, with possible discard
exposure if it is replaced. An opponent's active Item lock removes Field
Blower, Lost Vacuum, and Trainers' Mail as play routes. A held Lost Vacuum
also requires a second hand card to put into the Lost Zone.

This candidate deserves paired-seat, varied-opponent testing under a pinned
simulator with a validated card policy before it can replace the published
tournament list as a competitive recommendation.
