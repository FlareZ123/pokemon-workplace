# Regidrago's Legacy Star as a natural-only second-gust rescue line

## Question

A previous [sequential gust study](../regidrago_double_gust_access/) found that after spending the sole Guzma from the experimental Regidrago deck on turn one, an Item lock on turn two blocks VS Seeker, Prime Catcher and Counter Catcher. It explicitly omitted the **Legacy Star** VSTAR Power, which can return that spent Guzma from discard to hand even during an Item lock, provided its Ability and Supporter play remain available.

How frequently does the *published exact 60-card composition*, without assuming a magically established VSTAR, naturally hold the structural ingredients for that route by the start of its second turn?

## Necessary physical-card access event

With the going-second player able to play a T1 Supporter:

- A uniformly shuffled seven-card initial hand contains at least one Basic Pokémon, from **15** total (four Regidrago V and eleven other Basics).
- Six Prize cards are set aside uniformly, then one natural card is drawn on T1.
- At that point the player holds **at least one Regidrago V and one Guzma**. The player can establish the Basic V and use Guzma that turn, assuming an opposing Bench target and sufficient own board availability.
- A second natural draw occurs on T2. At least one of the three **Regidrago VSTAR** copies is then in hand, so an established V may evolve and use **Legacy Star**, assuming the V survived, the VSTAR Power is unspent, Ability effects are allowed, and the effect can be used.

The event uses only direct physical possession. It excludes Quick Ball, Mysterious Treasure, all Supporter-driven draw, Battle Compressor, Legacy Star deck milling effects beyond its retrieval, and search chains. Those omitted paths can greatly increase real T2 VSTAR access, while board failure or Ability locks can invalidate it. Thus the result is a **restricted incidence certificate**, with no generic upper/lower-bound claim for real games.

## Exact results for real Aichi card counts

| 60-card candidate | T1 V + Guzma, T2 VSTAR naturally available |
| --- | ---: |
| Published Yoshioka 2-Guzma list | **3.744430985%** |
| Experimental −1 Guzma/+1 Counter Catcher | **1.963672777%** |

The one-card substitution reduces the naturally executable **V + Guzma → VSTAR Legacy Star** source configuration by **1.780758209 percentage points**, a factor of approximately **1.91** in favor of the original for this event. Since the extra Counter Catcher is non-Basic and does not replace the four Regidrago V, three VSTAR or other eleven Basics, it acts as filler relative to this event.

The previously described `legacy_ready=True` game-state case produces a guaranteed second-turn Guzma recovery if the first-turn Guzma was spent and both Legacy Star and the second-turn Supporter are available. This experiment quantifies one conservative **natural route toward reaching that readiness**. The two percentages must not be interpreted as independent opportunities to add to the other source-access probabilities: the events overlap and the game-state conditions differ.

## Reproduction and independent oracle

The [exact rational solver](../../tools/regidrago_legacy_star_launch.py) separately counts other Basics, Regidrago V Basics, VSTAR evolution cards, Guzma Supporters, and filler. It conditions the opening hand on containing at least one Basic, enumerates two ordered natural draws without replacement, and marginalizes uniformly random six-card Prizes. The exact open-hand/Prize joint count is preserved through this marginalization.

The [independent reproducer](reproduce.py) instead physically enumerates all labeled opening hands, explicitly selected Prize sets and ordered first/second draws in **eight** differently composed ten-card toy deck populations. Every toy exact Fraction agrees with the analytic solver. It also checks the original/swap 60-card construction and print eligibility, the printed Regidrago V Basic identity, and the exact `swsh12-136` **Legacy Star** discard-to-hand effect.

Reproduce from repository root: `python -m results.regidrago_legacy_star_launch.reproduce`.

## Practical implication

It is dangerous to describe the swapped list as unable to gust on T2 under Item lock after spending Guzma on T1. Legacy Star can rescue the situation, and the original Regidrago VSTAR engine has the potential to make this route accessible via its other search/draw tools. At the same time, the original's second Guzma improves the chance of naturally establishing the prerequisite first-turn Guzma plus T2 VSTAR line. The **published original remains the stronger evidence-based competitive baseline**, and no representative-field win-rate advantage has been demonstrated for the swap.
