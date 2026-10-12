# Regidrago VSTAR / two Dragapult ex | Experimental candidate

**Status:** Exact-print 60-card paper Expanded counterfactual derived from Haruku Yoshioka's 2026 Aichi 10th-place list. This was **not** the published tournament composition. It changes only +1 Dragapult ex (`sv6-130`) and -1 Battle VIP Pass (`swsh8-225`). The original [published reference](../regidrago-vstar/) remains unchanged.

### Pokémon (21)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Regidrago V | `swsh12-135` |
| 3 | Regidrago VSTAR | `swsh12-136` |
| 2 | Budew | `sv8pt5-4` |
| 2 | Dragapult ex | `sv6-130` |
| 1 | Dialga-GX | `sm5-100` |
| 1 | Koraidon ex | `sv5-120` |
| 1 | Kyurem | `sv6pt5-47` |
| 1 | Hisuian Goodra VSTAR | `swsh11-136` |
| 1 | Dedenne-GX | `sm10-57` |
| 1 | Squawkabilly ex | `sv2-169` |
| 1 | Tapu Lele-GX | `sm2-60` |
| 1 | Latias ex | `sv8-76` |
| 1 | Marshadow | `sm10-81` |
| 1 | Wobbuffet | `xy4-36` |

### Trainer (29)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Professor's Research | `sv8pt5-122` |
| 2 | Guzma | `sm3-115` |
| 1 | Iono | `sv2-185` |
| 1 | Carmine | `sv6-145` |
| 1 | Lillie's Determination | `me1-119` |
| 1 | Marnie | `swsh1-169` |
| 1 | Raihan | `swsh7-152` |
| 1 | Crispin | `sv7-133` |
| 1 | Faba | `sm8-173` |
| 3 | Quick Ball | `swsh1-179` |
| 3 | Mysterious Treasure | `sm6-113` |
| 2 | Battle VIP Pass | `swsh8-225` |
| 3 | VS Seeker | `xy6-110` |
| 1 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Battle Compressor Team Flare Gear | `xy4-92` |
| 1 | Super Rod | `sv2-188` |
| 1 | Prime Catcher | `sv5-157` |
| 2 | Muscle Band | `xy1-121` |
| 1 | Parallel City | `xy8-145` |

### Energy (10)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Double Dragon Energy | `xy6-97` |
| 4 | Grass Energy | `bw1-105` |
| 2 | Fire Energy | `bw1-106` |

**Count verified:** 60 cards; 21 Pokémon / 29 Trainers / 10 Energy; one ACE SPEC (Prime Catcher). The [complete manifest](candidate.json) preserves the original exact-print identities and provenance. [Independent legality/change regression](reproduce.py).

## Evidence and limits

An [exact joint first-turn Item study](../../regidrago_joint_launch/) found **19.536020%** for Regidrago V source access **and** discarded Dragapult ex under its D=0 approved-payment policy, versus **13.257301%** for the published list. The [K0 first-Item action study](../../regidrago_k0_joint_launch/) reproduced both endpoints without relying on choosing a different first Item according to unknown Prizes. The experimental list trades away one VIP Pass and lowers marginal Regidrago V source access. Neither result models Regidrago VSTAR evolution, Energy supply, Phantom Dive execution, matchup interactions or full matches.

**Interpretation:** Promising candidate for targeted two-turn and head-to-head testing; **competitive superiority is unproven**. Compare against Shadow Rider, Vileplume control, Mew/Genesect, and ability-lock opponents with a reproducible opponent distribution.

## Natural two-turn Energy window

Apex Dragon has printed cost **Grass, Grass, Fire**. One **Double Dragon Energy**, which supplies two units of any Energy type on a Dragon Pokémon, plus a Grass Energy, Fire Energy, or second Double Dragon Energy supports this attack with two ordinary manual attachments. With only the seven-card opener and one ordinary draw on each of the first two own turns, at least one of those Energy cards must be in hand on turn one; a second qualifying Energy card may arrive on turn two.

The [exact natural-Energy exposure model](../../../tools/regidrago_two_turn_natural_energy.py) checks this event with 15 Basic opening Pokémon, four Double Dragon Energy, four Grass Energy and two Fire Energy in the 60. Conditional on a valid seven-card opener, **32.651714301%** of games have such a pair among the nine naturally exposed cards. Accepted-opening probability itself is **88.249920535%**. The published list and this +Dragapult/−VIP counterfactual have identical starter and Energy counts, so **the natural Energy-pair exposure probability is unchanged by the proposed swap**.

[The independently physical-opening/Prize/draw regression](energy_readiness_reproduce.py) passed [manual Windows CI](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293309042). This is natural material availability only. It omits Supporters including Crispin, extra Ability draws, search, Item acceleration, Energy survival, evolve/attack sequencing, and opposing interaction; actual turn-two Apex Dragon readiness can be higher or lower than the source-only percentage.
