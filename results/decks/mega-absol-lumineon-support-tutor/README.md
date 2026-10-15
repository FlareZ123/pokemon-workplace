# Mega Absol ex / Garbodor with Lumineon V (experimental 60)

**Evidence status:** A one-card paper Expanded counterfactual derived from Yusuke Kobayashi's eighth-place Aichi Open League list, 10 May 2026. This variant was not the published tournament list and has no observed match-win evidence.

**Exact change:** swap one `swsh3-104` Crobat V for one `swsh9-40` Lumineon V. Keep the two Mega Absol ex, one Tapu Lele-GX, Forest Seal Stone, Adventure Bag, both Temple of Sinnoh, all eight printed Supporters, seven Energy and all other 59 physical cards unchanged.

**Full playable list:** The table below lists all 60 representative English prints, with a machine-readable [print-level JSON manifest](deck.json) for independent validation. The [published Crobat reference](../mega-absol-garbodor/) is retained separately. The reproducer verifies that the proposed list differs in exactly this one slot and passes the repository's October 15, 2026 paper Expanded snapshot construction test.

## Complete 60-card list

### Pokémon (12)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Mega Absol ex | `me1-86` |
| 2 | Trubbish | `bw11-67` |
| 2 | Garbodor | `bw11-68` |
| 1 | Tapu Koko ◇ | `sm9-51` |
| 1 | Dedenne-GX | `sm10-57` |
| 1 | Lumineon V | `swsh9-40` |
| 1 | Squawkabilly ex | `sv2-169` |
| 1 | Tapu Lele-GX | `sm2-60` |
| 1 | Budew | `sv8pt5-4` |

### Trainer (41)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 1 | Lillie's Determination | `me1-119` |
| 1 | Carmine | `sv6-145` |
| 1 | Iono | `sv2-185` |
| 1 | Roxanne | `swsh10-150` |
| 1 | Guzma | `sm3-115` |
| 1 | Crispin | `sv7-133` |
| 1 | Wally | `xy6-94` |
| 1 | Karen | `xyp-XY177` |
| 4 | Quick Ball | `swsh1-179` |
| 4 | Dark Patch | `swsh10-139` |
| 3 | VS Seeker | `xy6-110` |
| 2 | Battle Compressor Team Flare Gear | `xy4-92` |
| 2 | Ultra Ball | `swsh9-150` |
| 2 | Battle VIP Pass | `swsh8-225` |
| 1 | Boost Shake | `swsh7-142` |
| 1 | Secret Box | `sv6-163` |
| 1 | Night Stretcher | `sv6pt5-61` |
| 1 | Super Rod | `sv2-188` |
| 1 | Pokémon Communication | `sm9-152` |
| 1 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Field Blower | `sm2-125` |
| 1 | Adventure Bag | `sm8-167` |
| 4 | Float Stone | `xy8-137` |
| 1 | Muscle Band | `xy1-121` |
| 1 | Forest Seal Stone | `swsh12-156` |
| 2 | Temple of Sinnoh | `swsh10-155` |

### Energy (7)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 5 | Darkness Energy | `bw1-111` |
| 2 | Lightning Energy | `bw1-108` |

## Why this particular swap?

Tapu Lele-GX's **Wonder Tag** and Lumineon V's **Luminous Sign** each search for a Supporter when the Pokémon is played **from hand onto the Bench**. A held first-turn Supporter is already usable without either tutor; including both effects can overstate their additional value. This analysis therefore evaluates the union of the eight actual Supporter cards printed in the published list.

Crobat V's **Dark Asset** instead draws until the hand has six cards when played from hand to Bench. It can find arbitrary missing cards and discard payments, making the original tournament slot strategically valuable even when a Supporter is already available. The exchange is not a confirmed competitive improvement.

Lumineon is also a Pokémon V and therefore remains a host for the deck's existing Forest Seal Stone **Star Alchemy**. Both lines occupy a vulnerable two-Prize Bench slot and share active Ability-lock problems under Garbotoxin. The existing [single-Crispin](../../absol_lumineon_supporter_frontier/) and [Crispin-plus-Stone](../../absol_lumineon_stone_overlap/) studies cover different, narrower material endpoints.

## Restricted access study

See [the eight-Supporter physical experiment](../../tests/absol_lumineon_any_supporter/) for the precise assumptions and reproduced results. Its success condition is having **any** of the eight named Supporter cards in hand by the first natural draw or one payable Basic-tutor Item followed by a hand-to-Bench Tutor Ability. It accounts for a seven-card Basic-valid hand, six Prizes, start-Active constraint, search target Prizing, Quick/Ultra Ball Energy-only discards, Pokémon Communication's spare Pokémon, and Hisuian Heavy Ball. Battle VIP Pass directly placing a tutor from deck does not trigger Wonder Tag or Luminous Sign.

A [joint eight-Supporter plus Forest Seal Stone analysis](../../tests/absol_any_supporter_stone/) further reduces the restricted Lumineon gain from **3.997939 to 3.185402 percentage points**, because both Crobat and Lumineon can use Star Alchemy. These figures remain conditional material-access measurements.

This is an opening material-access model with a selected line of play, no opponent, no later turn, no Ability-lock timing, no Crobat draw and no actual matchup win rate. The source Aichi eighth-place 60 remains the stronger supported tournament starting point.
