# Aichi 2026 Regidrago: Grass versus Fire expenditure before Trifrost

**Evidence class:** exact source-backed, conditional finite-deck combinatorics with an independent small-deck physical-card oracle. No win rates, turn-access rates, or actual opponent frequencies are estimated.

## Printed-list question

The published tenth-place CL2026 Aichi Regidrago list by Haruku Yoshioka has **four Grass Energy, two Fire Energy, four Double Dragon Energy, one Crispin, and one Kyurem**. Regidrago VSTAR (`swsh12-136`) uses the Grass/Grass/Fire Apex Dragon attack. On this Dragon, one Double Dragon Energy (`xy6-97`) and a Basic of *either* Grass or Fire provides the three typed units necessary to attack. Kyurem's (`sv6pt5-47`) copied Trifrost discards all Energy from the acting Regidrago.

Crispin (`sv7-133`) searches **up to two Basic Energy cards of different types** and can attach one to a Pokémon while putting the other into hand. This study asks: after discarding DDE and **either** one Grass or one Fire with Trifrost, how often can the deck still provide **both** Basic types for that full two-card Crispin search? This is a necessary stock condition for this specific two-type route, not proof the Supporter can or will be played.

## Defined probability model

Condition on the player having acquired and attached one DDE and one Basic Grass **or** Fire, which are subsequently discarded through Trifrost and are therefore outside the remaining unknown card pool. The other **58 physical cards** are initially unlocated. Place six Prize cards and an optional specified number of additional non-deck cards uniformly without replacement from those 58. The rest is treated as searchable deck.

After a Grass attachment, **3 Grass and 2 Fire** remain among the unknown 58. After a Fire attachment, **4 Grass and 1 Fire** remain. For total number `m` of unknown cards outside the searchable deck, and unknown type counts `g,f`, exact inclusion-exclusion gives:

`P(both types remain) = 1 - C(58-g,m-g)/C(58,m) - C(58-f,m-f)/C(58,m) + C(58-g-f,m-g-f)/C(58,m)`.

An impossible binomial choice has value zero.

| Additional uniformly placed non-deck cards | Place Grass first | Place Fire first | Grass advantage |
| ---: | ---: | ---: | ---: |
| 0 (only six Prizes) | 99.0279% | 89.6518% | +9.3761 pp |
| 3 | 97.5527% | 84.4558% | +13.0968 pp |
| 7 | 94.3825% | 77.4458% | +16.9367 pp |
| 10 | 91.0209% | 72.0801% | +18.9408 pp |
| 15 | 83.4296% | 62.8265% | +20.6030 pp |

The first row's exact probabilities are `13039/13167` (Grass) and `342329/381843` (Fire). The 13-card-outside case is `10921/11571` and `35845/46284`. For all 59 outside counts from 0 through 58, Grass-first weakly preserves two-type deck supply; it is strictly better at **56 of 59** counts, tied when `m=0,57,58`.

**These artificial cases are not actual gameplay rates.** The event of establishing DDE and a chosen Basic has not been given a probability. The model does not sample a real hand, real search decisions, prior Prize knowledge, turn sequencing, or observed zone states. It conditions on a uniform allocation of the remaining physically distinct cards, which actual play can select nonuniformly.

## Tactical significance and limits

The result gives a specific resource-conservation reason to prefer Grass over Fire when an otherwise interchangeable Basic Energy is used to pay Apex Dragon before a planned Trifrost. With only two Basic Fire Energy in the whole Aichi deck, discarding a Fire earlier can leave the later full Crispin search without its second type. In practice, preserving Fire may have other costs. Crispin **can still search one Basic Energy when only one type remains**, and alternative recovery/acceleration routes exist. The model explicitly prices none of these tradeoffs and does not suggest any 60-card slot changes.

## Reproduction

- [Source-verified calculator](../../../tools/aichi_regidrago_crispin_energy_supply.py) uses the complete published English-print Aichi manifest at `results/regidrago_aichi_top10_playable/yoshioka_regidrago_2026.json`.
- [Reproducer](reproduce.py) checks card texts and exact 60-count, validates all source figures, and independently enumerates **2,424** miniature physical-card deck/outside configurations against the formula.
- Command from repository root: `python -m results.tests.aichi_regidrago_crispin_post_trifrost.reproduce`.
- Tournament list: https://limitlesstcg.com/decks/list/26816 .

This is one narrowly conditioned decision feature for a realistic deck policy. Measuring how often the relevant game state occurs, whether Crispin can be accessed, and whether Grass conservation beats its competing uses requires a fuller sequential model.
