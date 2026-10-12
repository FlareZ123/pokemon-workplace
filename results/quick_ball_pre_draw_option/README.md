# Quick Ball pre-draw option: exact opening-conditioned comparison

## Question

Does preserving a payable Quick Ball until after one natural draw improve the chance of completing **both** attacker setup and Gladion access, even when its use is already clear before drawing?

The existing [opening allocation frontier](../quick_ball_allocation_frontier/) and [post-draw frontier](../quick_ball_allocation_draw_frontier/) quantify physical contention and the value of an additional observed card. The [one-draw microstate](../quick_ball_wait_option/) already proves an isolated option-value example. This experiment adds **an explicit eager-policy counterfactual over the entire accepted-opening and six-Prize distribution**.

The executable model is [quick_ball_pre_draw_option.py](../../tools/quick_ball_pre_draw_option.py), with an independent [labeled-card reproducer](reproduce.py).

## Deck categories and conditioning

The exact 60-card state model uses 1 required Basic attacker, 1 Tapu Lele-GX, 10 other eligible starters, 4 critical non-starter cards, 2 Gladion-like Supporters, 4 Quick Ball, a variable pool of designated disposable cards, and filler. It draws an opening 7, rejects mulligan hands without Basics, sets six random Prizes, then draws exactly one subsequent card. The reported rates condition on a valid opening and at least one of the four critical cards being Prized.

The two goals are `(attacker Basic established, Gladion accessible)`. They deliberately stop short of the full attack or rescue action. Every Quick Ball consumes one physical copy and one held designated disposable card. A searched Tapu Lele-GX enters hand and is then played onto the Bench for Wonder Tag. An opening Tapu Lele-GX used as the only setup Basic has lost its hand-to-Bench trigger. The target Basic or Gladion can be Prized and unavailable for search.

Official [Quick Ball](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/swsh8/237/) text requires a discarded hand card and searches one Basic Pokémon. The [current errata](https://play.pokemon.com/en-ca/resources/documents/tcg-errata/) supersedes the old randomized-search wording.

## Compared fixed policies

- **Wait:** do not spend Quick Ball before the natural draw; afterward allocate available copies and payments to finish both channels where possible.
- **Eager attacker:** if an executable Quick Ball has a still-missing purpose, spend one before drawing, searching for the attacker first; search Tapu Lele-GX instead when attacker setup is already complete.
- **Eager rescue:** the same rule, prioritizing the available Tapu Lele-GX route to Gladion, then attacker setup.

Early target selection depends on cards visible in the opening hand, including whether Tapu Lele-GX was consumed at setup. It does not choose its priority using latent Prize contents. A search can fail when its target was Prized. Any unspent Quick Ball copies remain available after the natural draw.

These are explicit comparison policies rather than globally optimized turn planners. The eager policies are forced to spend one usable connector before the draw when a modeled purpose is missing.

## Exact findings

| Dedicated disposable cards | Wait, joint | Eager attacker, joint | Eager rescue, joint | Wait advantage over stronger eager |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 10.662593% | 10.532042% | 10.244034% | 0.130551 pp |
| 8 | 14.762470% | 14.551300% | 14.080669% | 0.211170 pp |
| 12 | **17.755369%** | **17.498092%** | **16.919584%** | **0.257277 pp** |
| 16 | 19.867280% | 19.586458% | 18.950549% | 0.280822 pp |
| 20 | 21.294143% | 21.003420% | 20.341965% | 0.290723 pp |
| 24 | 22.204606% | 21.911313% | 21.242479% | 0.293293 pp |

The wait value at 12 disposable cards equals the independent [one-later-draw Pareto result](../quick_ball_allocation_draw_frontier/) to the displayed precision, 17.7553685868%.

The causal mechanism is information-dependent allocation. Drawing an attacker makes the attacker search redundant. Drawing Gladion or a functional unplayed Tapu Lele-GX makes the rescue search redundant. Retaining Quick Ball permits the remaining target to receive its search. Earlier searches can also thin the deck, and the eager comparator explicitly accounts for their physical target removal and the changed natural draw distribution.

At the D12 baseline, 28.152153% of conditioned states had a playable early Quick Ball with a modeled purpose. The benefit of preserving the decision across **all** conditioned states is smaller, 0.257277 percentage points, than the 13.658811-point opening either/or allocation mass studied in the earlier result.

## Validation and provenance

The exact engine enumerates opening category counts and disjoint Prize counts by multivariate combinations. It enumerates the seven post-Prize natural-draw categories, charges the selected Quick Ball and disposable resources, and accounts for early search removal of the attacker or Tapu Lele-GX plus Wonder Tag's searched Gladion.

The reproducer independently enumerates **physical labeled cards** for two toy models (11 and 12 cards), comparing all three policy rates to the categorical engine within `5e-12`. It separately checks the 60-card result against the previously published one-draw frontier baseline and asserts waiting weakly dominates both eager policies for each reported disposable-pool size. The test is automated in [the focused workflow](../../.github/workflows/validate-quick-ball-pre-draw-option.yml).

## Limits and research interpretation

This is a structural first-window comparison. The extra draw is supplied exogenously, as in the existing post-draw frontier. The model excludes opponent disruption, Item lock, Ability lock, a full Bench, Supporter contention, alternative Pokémon search Items, real discard opportunity costs, later Prize-taking, and direct attack execution.

The positive option value assumes the player can defer both objectives until after this natural draw. An attacker that must be set up **before** it cannot wait. The result is an exact conditional opening-access calculation, with no claim of measured competitive win rate or a recommended deck substitution.

A useful next test is to impose an attacker deadline before the draw and a later Gladion deadline in this same accepted-opening model, incorporating the previously isolated [deadline policy](../../tools/quick_ball_deadline_policy.py). That would quantify the price of forfeiting the observation in states that genuinely require early commitment.
