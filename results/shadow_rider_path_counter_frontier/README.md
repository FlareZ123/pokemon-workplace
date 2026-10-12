# Path to the Peak changes the Shadow Rider anti-Thorns frontier

## Mechanism

The 2026 Aichi champion Shadow Rider list contains one Field Blower, two Sky Field and one Dimension Valley. The separate [Cologne rescue study](../shadow_rider_cologne_thorns_counter/) and [Flutter Mane study](../shadow_rider_mixed_counter_frontier/) show how to remove the opposing Active Iron Thorns ex's Initialization suppression. Here we additionally require Path to the Peak to be in play on entry. Path suppresses Radiant Eternatus's Climactic Gate independently of Initialization.

A subtlety: **Path also turns off Iron Thorns ex's Initialization while Path is in play.** After Path is removed, Initialization activates again unless a Cologne or an Active Flutter Mane separately suppresses it. Thus two independent lock sources must be addressed to use Climactic Gate. Stadium replacement or Field Blower can remove Path, and Cologne or Flutter handles Thorns.

The champion also has one Forest Seal Stone. On Shadow Rider Calyrex V, its Tool-granted Star Alchemy VSTAR Power can obtain one missing role in this represented action window: Radiant Eternatus, Cologne, Field Blower or replacement Stadium. Its one use cannot simultaneously satisfy two missing roles.

## Real 60-card cut packages

Complete exact English print IDs, construction and conservative legal status are checked by [reproduce.py](reproduce.py), using the [published Aichi champion baseline](../competitive_deck_baselines/shadow_rider_reproduce.py). The following are counterfactual experiments; none of the cuts is yet recommended for competitive play.

| Counter cards added | Cards removed | Remaining usable Stadiums |
| --- | --- | ---: |
| None | None | 3 |
| 1 Cologne | 1 Sky Field | 2 |
| 1 Flutter Mane | 1 Sky Field | 2 |
| 2 Cologne | 2 Sky Field | 1 |
| 1 Cologne + 1 Flutter | 2 Sky Field | 1 |
| 2 Flutter | 2 Sky Field | 1 |
| 3 Cologne | 2 Sky Field + 1 Dimension Valley | 0 |
| 4 Cologne | 2 Sky Field + 1 Dimension Valley + 1 Night Stretcher | 0 |

The existing Field Blower remains present in every variant. The mixed two-slot complete decklist is provided by [the earlier study](../shadow_rider_mixed_counter_frontier/).

## Exact conditional first-turn results

Model: accepted opening seven with a Basic, six hidden Prizes, one natural first-turn going-second draw, two VMAX still available in the deck, an eligible opening Active, and physical resources to remove both Path and Thorns suppression. Held Mysterious Treasure may search Radiant for one discard, which is mechanically payable but strategically unpriced. Flutter must be in the initial seven to start Active; a Flutter drawn next is not considered switched in. Forest Seal Stone needs a V available from the first eight. No other tutors, draw or opponent actions are modeled.

| Counters added | No Path (previous model) | Path already in play |
| --- | ---: | ---: |
| None | 0.000000% | 0.000000% |
| 1 Cologne | 6.820639% | 1.974084% |
| 1 Flutter | 5.886766% | 1.841655% |
| 2 Cologne | 11.643271% | 2.490177% |
| **1 Cologne + 1 Flutter** | **11.981889%** | **2.622360%** |
| 2 Flutter | 11.006152% | 2.507258% |
| 3 Cologne | 15.830381% | 1.974084% |
| 4 Cologne | 19.570259% | 2.479023% |

The equality of **one-Cologne and three-Cologne** Path-present access is exact under this model. The first variant has one Cologne alongside three Path answers (two Stadiums and Field Blower); the second has three Cologne alongside only one Path answer (Field Blower). The two mandatory card roles are symmetric under card-label exchange, including the one available Forest Seal Stone search. This is a concrete demonstration of resource-channel contention.

Four Cologne has less restricted Path-present access than two Cologne and the retained Dimension Valley, even though four Cologne has greater access with no Path. The 1+1 mixed package stays slightly ahead among the two-slot cuts. No model here evaluates the tactical loss of Sky Field or actual opponent Path usage.

## Reproduction and limitations

The [source](reproduce.py) keeps physical Prize allocations of Radiant, VMAX, Cologne, Field Blower and usable Stadiums exact. It marginalizes irrelevant Prize classes and uses a provably equivalent order for the natural draw and Prize assignment after selecting the opener. A separate **41,328-world labeled-card oracle** deals opening → Prizes → draw chronologically, independently checking the resulting exact rational probabilities. Eight full 60-card print lists are adjudicated under the 2026-10-12 conservative Expanded snapshot.

The opponent going first can legally put a Stadium into play during its first turn, so this Path-present state can arise before Shadow Rider's first going-second turn. Results still condition on that specific opponent choice and do not estimate its frequency. Path, Item or Tool locks, alternate Standard/Expanded card interpretations, opposing counterplay, Bench congestion, K1 search information, future turns and actual match win rates all need additional modeling. In particular, this solver assumes no additional Item or Tool lock, and no effect removing Flutter's Ability.


## Extension: exhaustive two-counter mixtures for every 0–4-slot package

[Robustness reproducer](robustness.py) enumerates all **15** combinations of Cologne (C) and Flutter (F) consuming up to four slots under the same sequential cut rule. Every complete 60-card variant passes the exact-print construction and legality checks. All exact rational endpoint values are independently recomputed.

| Total slots spent | Mix C / F | Replacement Stadiums left | Path-present access |
| ---: | --- | ---: | ---: |
| 0 | 0 / 0 | 3 | 0.000000% |
| 1 | 1 / 0 | 2 | **1.974084%** |
| 1 | 0 / 1 | 2 | 1.841655% |
| 2 | 2 / 0 | 1 | 2.490177% |
| 2 | **1 / 1** | 1 | **2.622360%** |
| 2 | 0 / 2 | 1 | 2.507258% |
| 3 | 3 / 0 | 0 | 1.974084% |
| 3 | 2 / 1 | 0 | 2.045828% |
| 3 | **1 / 2** | 0 | **2.089297%** |
| 3 | 0 / 3 | 0 | 2.017595% |
| 4 | 4 / 0 | 0 | 2.479023% |
| 4 | 3 / 1 | 0 | 2.546091% |
| 4 | 2 / 2 | 0 | 2.598020% |
| 4 | **1 / 3** | 0 | **2.626431%** |
| 4 | 0 / 4 | 0 | 2.550910% |

The best **three-slot** package is **worse** than the best two-slot package: 2.089297% versus 2.622360%. Any third swap spends the deck's final replacement Stadium, leaving only Field Blower as the Path answer.

Four-card packages sometimes recover the loss through increased counter redundancy, yet the best four-card result, one Cologne plus three Flutter, gains only **0.004071 percentage points** over the best two-card package. That is an extremely small improvement in this specific launch-access endpoint for spending two additional deck slots, including Dimension Valley and Night Stretcher. Their other strategic functions were excluded.

This is a reproducible, exact **nonmonotonic optimization frontier with mutually dependent search roles**. It is a counterexample to a heuristic that keeps adding cards because one marginal access metric improves when considered without the displacement effects.
