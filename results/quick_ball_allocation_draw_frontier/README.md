# Post-draw Quick Ball allocation frontier

## Question

The opening-window frontier in `results/quick_ball_allocation_frontier/` identifies states where one physical Quick Ball can serve either attacker setup or Tapu Lele-GX for Gladion access, while insufficient search capacity prevents both.

How does that decision frontier change as the player sees additional random cards before the relevant action window?

Implementation: `tools/quick_ball_allocation_draw_frontier.py`  
Reproducer: `results/quick_ball_allocation_draw_frontier/reproduce.py`

## Model

The deck and conditioning match the opening-window frontier:

- 60 cards;
- 6 Prize cards;
- accepted 7-card opening;
- 1 Tapu Lele-GX;
- 1 required Basic attacker;
- 10 other setup-eligible starters;
- 4 modeled critical non-starter singletons;
- 2 Gladion-like rescue Supporters;
- 4 Quick Ball;
- 12 dedicated disposable non-starters;
- filler cards.

The calculation conditions on a valid opening and at least one modeled critical singleton being Prized.

After setup and Prize placement, the model exposes a specified number of unbiased random cards from the post-Prize deck. It then constructs the Pareto frontier over:

`(attacker established, Gladion accessible)`

Later-drawn copies can change the state in several ways. The attacker may arrive directly. Gladion may arrive directly. Tapu Lele-GX may arrive and enable Wonder Tag. Quick Ball or a disposable payment card may arrive. Drawing a search target also removes that target from the searchable deck.

Quick Ball still consumes one physical copy and one designated disposable card per search.

## Main result

| Later random draws | Both | Choice | Attacker only | Gladion only | Neither |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 13.057113% | 13.658811% | 10.560723% | 21.853400% | 40.869952% |
| 1 | 17.755369% | 14.630831% | 10.711527% | 22.604147% | 34.298127% |
| 2 | 22.805219% | 14.976722% | 10.684420% | 22.877807% | 28.655833% |
| 3 | 28.028588% | 14.809799% | 10.520220% | 22.783210% | 23.858183% |
| 5 | 38.417863% | 13.416871% | 9.914954% | 21.845727% | 16.404585% |
| 8 | 52.469061% | 10.154705% | 8.667740% | 19.503755% | 9.204739% |
| 12 | 66.863793% | 5.986793% | 6.916379% | 16.085344% | 4.147691% |

The zero-draw row exactly reproduces the opening-window frontier.

## Finding 1: connector contention is non-monotone under added information

The either/or choice frontier rises from **13.658811%** at zero later draws to **14.630831%** after one draw and **14.976722%** after two.

It then declines, reaching **13.416871%** after five draws, **10.154705%** after eight, and **5.986793%** after twelve.

An exact scan from zero through fifteen later draws places the largest choice mass in that scanned range at two draws.

This behavior has a direct state interpretation.

Early draws rescue some states from the neither frontier by supplying Quick Ball, a disposable payment, or one missing target. Some of those newly live states still have only enough connector capacity for one of the two channels, so choice mass can initially grow.

With more exposure, direct attacker draws, direct Gladion draws, and additional connector resources increasingly move states from the choice frontier into the both frontier. The allocation conflict then shrinks.

A fixed connector-contention penalty cannot represent this evolution.

## Finding 2: joint feasibility rises faster than the choice frontier

The physically joint `((1,1),)` mass rises from **13.057113%** at zero draws to:

- **17.755369%** after one draw;
- **22.805219%** after two;
- **38.417863%** after five;
- **66.863793%** after twelve.

The either/or frontier is therefore temporary option value. It is most prominent while the state has enough resources to expose competing uses but still lacks enough resources to complete both.

This suggests a useful distinction for finite-horizon planners:

- inaccessible states;
- allocation states;
- jointly feasible states.

Random exposure can move probability mass through all three classes over time.

## Finding 3: the Gladion projection exactly matches the independent access model

For each tested draw count, sum every frontier that contains a Gladion-accessible outcome:

`P(Gladion possible) = P(both) + P(choice) + P(Gladion only)`

The result exactly matches the strict `Quick Ball -> Tapu Lele-GX -> Gladion` probabilities from `results/quick_ball_lele_draw_access/`.

Examples:

| Later draws | Frontier Gladion projection | Independent strict access model |
| ---: | ---: | ---: |
| 0 | 48.569324% | 48.569324% |
| 1 | 54.990346% | 54.990346% |
| 2 | 60.659748% | 60.659748% |
| 5 | 73.680461% | 73.680461% |
| 8 | 82.127521% | 82.127521% |
| 12 | 88.935930% | 88.935930% |

The two tools reach these values through different output representations. Their equality is a useful cross-check on the setup, Prize, draw, and Quick Ball semantics.

## Finding 4: more access can temporarily create more strategic contention

It is tempting to assume that drawing more cards simply relaxes resource conflicts.

The first two draws do increase joint success, yet they also increase the probability that the player faces a meaningful allocation choice between attacker setup and Gladion access.

This is a form of revealed option value. A resource can become more strategically contested after the hand improves because the new card makes several competing lines simultaneously realistic.

The effect supports a state-dependent treatment of connector domination. Opportunity cost depends on which alternative uses are actually live at the decision time.

## Validation

The model is exact and uses no Monte Carlo sampling.

The reproducer independently enumerates a labeled ten-card deck over:

- every accepted three-card opening;
- every disjoint two-card Prize set;
- every disjoint two-card later-draw set.

It reconstructs the physical Quick Ball allocation frontier and matches the category model to floating-point precision.

The reproducer also verifies two cross-model reductions:

1. zero later draws reproduce `tools/quick_ball_allocation_frontier.py` exactly;
2. the Gladion projection matches `tools/quick_ball_lele_draw_access.py` exactly at every reported draw count.

## Limits

The model treats later exposure as unbiased random draws. Targeted search and shuffle-draw effects need their own transitions.

The required attacker channel is complete once a Basic attacker is available to establish. The model does not include Energy, evolution, switching, attack timing, Bench saturation, Item lock, Ability lock, competing Supporters, ordinary Prize-taking, or opponent interaction.

The non-monotonic peak claim is intentionally limited to the exact zero-through-fifteen scan. A full zero-through-forty-seven sweep was computationally expensive in the current implementation and was not used as evidence.

## Next useful work

The next extension should attach separate deadlines to the two frontier coordinates.

An attacker may need to be established immediately while a Prized singleton can remain recoverable later. Carrying this frontier into a finite-horizon policy would measure when the player should spend Quick Ball now, preserve it for future information, or redirect it after one channel arrives naturally.
