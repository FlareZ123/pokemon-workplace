# Shadow Rider Calyrex VMAX: two single-slot anti-Iron-Thorns experiments

**Status: experimental, legal-print candidate lists.** The source is the [2026 Aichi champion Shadow Rider Calyrex list](../shadow-rider-calyrex/), with exactly one card changed. Neither variant has tournament placement, head-to-head matchup results or a measured win rate. Current date: 15 October 2026.

Both alternatives remove the **second Lillie's Clefairy ex (sv9-56)** and replace it with one Basic Psychic counter. The sacrifice may hurt the Dragon matchup, Prize resilience, or draw options; that tradeoff is unmeasured. This is a targeted research baseline for Iron Thorns, with all remaining champion slots intact.

## Variant A: Flutter Mane (one-card swap)

Add **1 Flutter Mane sv5-78**, remove **1 Lillie's Clefairy ex sv9-56**. Flutter Mane's Active Midnight Fluttering suppresses the opposing Active Iron Thorns ex while preserving Radiant Eternatus's Climactic Gate. It must survive and remain Active for suppression to persist.

## Variant B: Wobbuffet (one-card swap)

Add **1 Wobbuffet xy4-36**, remove **1 Lillie's Clefairy ex sv9-56**. Active Bide Barricade suppresses opposing Iron Thorns ex and permits Underworld Door because Shadow Rider VMAX is Psychic. It simultaneously disables Dragon Radiant Eternatus's Climactic Gate while Wobbuffet remains Active. Thus Wobbuffet is a potential continuation counter after a VMAX exists, not a direct substitute for Flutter in the champion's immediate Radiant launch route.

## Both complete 60-card lists

The quantities are identical across A and B except for the final two Pokémon rows. Each variant is **18 Pokémon, 31 Trainers and 11 Energy**.

### Pokémon (18 per variant)

| Qty A | Qty B | Pokémon | Representative English print ID |
| ---: | ---: | --- | --- |
| 3 | 3 | Shadow Rider Calyrex V | swsh6-74 |
| 4 | 4 | Shadow Rider Calyrex VMAX | swsh6-75 |
| 1 | 1 | Lillie's Clefairy ex | sv9-56 |
| 2 | 2 | Tapu Lele-GX | sm2-60 |
| 1 | 1 | Trevenant & Dusknoir-GX | smp-SM217 |
| 1 | 1 | Latias ex | sv8-76 |
| 1 | 1 | Dialga-GX | sm5-100 |
| 1 | 1 | Mimikyu (Copycat) | sm2-58 |
| 1 | 1 | Girafarig | sm8-94 |
| 1 | 1 | Marshadow (Resetting Hole) | sm10-81 |
| 1 | 1 | Radiant Eternatus | swsh12pt5-105 |
| 1 | 0 | Flutter Mane (Midnight Fluttering) | sv5-78 |
| 0 | 1 | Wobbuffet (Bide Barricade) | xy4-36 |

### Trainers (31 per variant)

| Qty | Trainer | Representative English print ID |
| ---: | --- | --- |
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
| 2 | Sky Field | xy6-89 |
| 1 | Dimension Valley | xy4-93 |

### Energy (11 per variant)

| Qty | Energy | Representative English print ID |
| ---: | --- | --- |
| 11 | Basic Psychic Energy | bw1-109 |

## Why these two alternatives

Both techs are Basic Psychic Pokémon with the same one-card slot cost and are searchable in principle by existing Fog Crystal, Mysterious Treasure or Quick Ball. Those shared search connectors can be needed for the core attacking engine, and Mysterious Treasure and Quick Ball require real discard payment. Search reachability alone does not prove the tech can be accessed at the right time.

Either variant retains 14 Basics and therefore the same **86.140932% Basic-valid probability** for a uniformly dealt initial seven as the champion source. With one specific Basic tech, the probability of drawing it naturally in that seven conditional on a valid opener is **13.543697%**. This is an opening-hand visibility statistic, not a probability of entering the Active Spot while Thorns is live.

The [Wobbuffet/Flutter exact-board regression](../../wobbuffet_flutter_thorns_continuation/) validates different lock and Radiant Eternatus interactions under Iron Thorns; it does not test full game sequencing.

## Verification and status

The runnable proof [reproduce.py](reproduce.py) reconstructs the original published champion 60 from its source fixture, makes precisely one indicated swap, verifies both printed lists, and invokes the repository's print-aware paper Expanded legality adjudicator for the current snapshot. CI runs this proof independently.

Neither variant has measured expected match win percentage. In particular, the lost second Clefairy, the chance of opposing Stealthy Hood, Wobbuffet's incompatibility with Radiant launch, Bench space, Active mobility and opponent's first-attack timing can all reverse an apparent one-card benefit. Retain the published champion as the tournament-supported default pending real matchup evidence.
