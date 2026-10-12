# Exact Regidrago V + Guzma → Legacy Star with paid Item searches

## Competitive deck question

The 2026 Aichi Open League 10th-place [published 60-card Regidrago VSTAR](../competitive_deck_baselines/) has **4 Regidrago V**, **3 Regidrago VSTAR**, **2 Guzma**, **3 Battle VIP Pass**, **3 Quick Ball**, **3 Mysterious Treasure** and **15 starting Basic Pokémon**. Its [legal one-slot Counter Catcher candidate](../aichi_regidrago_gust_deadlines/regidrago_counter_catcher_60.txt) changes one Guzma into Counter Catcher and retains all 59 other prints. Both contain Regidrago VSTAR's **Legacy Star**, which can recover an already played Guzma without using an Item, provided its VSTAR Power is available and relevant Abilities and Supporters are legal.

The prior [natural-only exact result](../regidrago_legacy_star_launch/) measured the physical event that the player holds Regidrago V and Guzma by its first own turn going second and also holds Regidrago VSTAR by turn two. That event is only **3.744430985%** in the published 60 and **1.963672777%** in the swap. This study adds actual **search sources, costs, Prizes, and search-induced deck thinning** without assuming the complete attacker and disruption game is already established.

## Declared action policy

From a uniformly shuffled deck, accept only a seven-card opening containing a Basic Pokémon, set six random face-down Prize cards aside, and make one natural draw at the start of each own turn. We assume the player goes second so using Guzma on T1 is allowed. The route requires:

1. Naturally hold and play Guzma on T1, with an opponent's Bench target that makes the Supporter playable. Its physical card goes to discard.
2. Establish Regidrago V on T1: use a held copy first, otherwise Battle VIP Pass to put one deck-resident V directly onto the Bench, otherwise Quick Ball with one approved discard card, otherwise Mysterious Treasure with one approved discard card. T1 Item permission is an external input.
3. Obtain Regidrago VSTAR by T2: keep a held copy, otherwise use a remaining T1 Mysterious Treasure with one approved discard to **prefetch** a deck-resident VSTAR, otherwise draw it naturally on T2 or pay a T2 Mysterious Treasure after the draw. T2 Item permission is separate. Every V/VSTAR search checks that its target is physically in the deck, outside hand and Prizes. It removes the target and reshuffles the remaining deck, so the next draw comes from the correct post-search population.
4. Assume the V survives to evolve on T2, Legacy Star is unspent and unblocked, and Supporter play remains permitted. Legacy Star can then retrieve the Guzma already in discard, opening a possible second turn of gust.

`D` represents the number of explicitly **approved disposable non-Basic filler cards** included in the 60. Only a held D card may pay Quick Ball or Mysterious Treasure in this policy, and every payment consumes an individual physical D. The original list contains 31 other copies outside the modeled eight named categories, including Prime Catcher; the protected remainder always retains at least one card. For the swap, the Counter Catcher occupies the removed Guzma's protected filler slot. D=0, 10, and 20 are **sensitivity assumptions** about strategic discardability, not observed properties or a recommendation to discard arbitrarily.

The route is a **conditional material-access event**, and it assumes suitable Bench space and a playable Guzma target. It does not enforce the opponent's active Pokémon survival, turn-specific board actions, Energy requirements, search disruption, other card draw, Tapu Lele-GX's Wonder Tag, actual Timeless-GX attack timing, or whether Legacy Star is strategically better spent elsewhere.

## Exact probabilities

Probability of the whole **T1 Guzma + T1 Regidrago V + T2 Regidrago VSTAR** material route, conditional on a Basic-valid opening (six random Prizes):

| Approved discard pool | T1 Item permission | T2 Item permission | Published two Guzma | Experimental one Guzma |
| ---: | :---: | :---: | ---: | ---: |
| D=0 | Blocked | Blocked | **3.744431%** | 1.963673% |
| D=0 | Allowed | Blocked | **5.119058%** | 2.683159% |
| D=0 | Allowed | Allowed | **5.119058%** | 2.683159% |
| D=10 | Blocked | Blocked | **3.744431%** | 1.963673% |
| D=10 | Allowed | Blocked | **8.689401%** | 4.545158% |
| D=10 | Allowed | Allowed | **9.353768%** | 4.896580% |
| D=20 | Blocked | Blocked | **3.744431%** | 1.963673% |
| D=20 | Allowed | Blocked | **10.278804%** | 5.383218% |
| D=20 | Allowed | Allowed | **10.990941%** | 5.762803% |

With D=10 and Items allowed T1 but locked T2, the source-specific policy raises published-list access from the natural-only **3.744431% to 8.689401%**, and raises the swap from **1.963673% to 4.545158%**. The exact marginal gain of additionally permitting T2 Items is **0.664368 percentage points** in the original and **0.351422 points** in the swap.

The published list maintains a higher absolute joint source-access probability in every controlled window because an extra naturally held Guzma can establish the T1 prerequisite, although the swap has its own future Prize-gated tactical advantages. The two variants have identical access to the other V/VSTAR search cards, so these results isolate one important opportunity cost of the proposed gust substitution.

## Exact derivation and checks

The [Fraction-valued source model](../../tools/regidrago_legacy_item_access.py) enumerates every possible first-eight-card multivariate composition in categories: eleven other Basics, four Regidrago V, three VSTAR, Guzma, VIP, Quick, Treasure, D and protected filler. It corrects the first-seven-cards-basic constraint by counting valid last-draw positions. For each composition, it enumerates the Prize counts of V and VSTAR by multivariate hypergeometric weights. Other Prize-card labels can be integrated out by symmetry.

After paying each Item and removing its searched target from the true deck, the remaining natural T2 draw has exact probability `remaining VSTAR / remaining deck cards` of revealing VSTAR directly. If T2 Treasure can be paid only when the single T2 draw finds a missing Treasure or D, the corresponding probabilities use a separate conditional hypergeometric ratio over non-V/non-VSTAR Prize identities. All outputs are exact fractions; the table is their rounded decimal presentation.

The [single runnable regression](reproduce.py) independently enumerates fully labeled physical cards, legal three-card toy openings, genuine two-card Prize selections and both natural draws after physically removing searched cards. **12 different miniature deck/Item-window configurations** agree with the exact category model. Two independent 60-card no-Item reductions exactly equal the previous Legacy Star natural-access solver. The regression checks the actual printed texts of Quick Ball (`swsh1-179`), Battle VIP Pass (`swsh8-225`), and Mysterious Treasure (`sm6-113`), and the baseline/variant legality proof.

Run at repository root: `python -m results.regidrago_legacy_item_access.reproduce`. The Windows validation workflow is manually dispatched to preserve the shared CI budget.

## Deck-building consequence

This is a stronger material-access comparison than simple “one fewer gust card”, because it includes named search connectors, their discard costs, specific early windows, random Prizes, and later T2 deck access. It is still far short of a credible matchup win-rate experiment. A next step is to account for first-turn Tapu Lele-GX → Supporter acquisition, including Wonder Tag being blocked by Iron Thorns ex or other Ability locks, and to attach the material route to real opposing board targets, VSTAR survivability, and Prize clocks. The published tournament two-Guzma list remains the best-grounded baseline pending such comparisons.
