# Fixed-slot optimization of Arc, Peonia and top-five arranging Items

## Research question

If a toy 60-card Expanded deck devotes `K` slots to a narrow target-acquisition sequence, how should those slots be divided between Arc Phone, Peonia, and top-five deck-arranging Items? This tests connector-capacity complementarity by **holding total tech-package size fixed** rather than assuming every connector can be added without sacrificing another card.

The success event and its exact opening/normal-draw combinatorics are detailed in [Rotom–Arc–Peonia incidence](../rotom_arc_peonia_incidence/). A target T must be exactly next on deck top and an Arc and Peonia plus filler available, or T can be among the next five cards if a top-five arranger is available. A player going second may execute these Items and Peonia in one turn under the ordinary rules.

## Constrained optimization

Keep twelve Basic starters, one critical non-Basic singleton T and a fixed 60-card total. Allocate `K=A+P+R` slots with:

- `1 <= A <= 4` Arc Phone copies;
- `1 <= P <= 4` Peonia copies;
- `0 <= R <= 8` top-five arranging Items: up to four Rotom Phone plus four differently named Pokédex;
- `F=47-K` other cards, all assumed expendable Peonia payments.

Each allocation's success probability is computed exactly by a rational multivariate-hypergeometric model conditioned on at least one Basic in the *first seven* and the mandatory first-turn draw. Every allowable allocation in each fixed `K` is enumerated and the exact maximum selected. Swapping A and P preserves the mathematical event, so tied mirror optima are equivalent in this **narrow** model.

## Exact optimal allocation frontier

| Package K | Arc (A) | Peonia (P) | Top-five Items (R) | Optimal raw event probability |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 1 | 0 | 0.024432% |
| 4 | 2 | 2 | 0 | 0.088513% |
| 6 | 3 | 3 | 0 | 0.180284% |
| 7 | 3 | 3 | 1 | 0.252125% |
| 8 | 4 | 3 | 1 | 0.320633% |
| 9 | 4 | 4 | 1 | 0.407570% |
| 10 | 4 | 4 | 2 | 0.515200% |
| 12 | 4 | 4 | 4 | 0.703037% |
| 16 | 4 | 4 | 8 | 0.983472% |

The complete reproducible table includes each integer K from 2 through 16. The **first optimal top-five Item occurs at K=7**. With K=6, the balanced 3 Arc + 3 Peonia package attains 0.180284%, whereas adding a top-five Item to 3 Arc + 2 Peonia reaches only 0.176260%. With K=7, 3 Arc + 3 Peonia + 1 arranger reaches 0.252125%, surpassing 4 Arc + 3 Peonia with no arranger (0.228714%).

This is a concrete conditional manifestation of connector complementarity: enhancing topdeck selection produces little value when the hand seldom contains the **other two different required actions**. The strongest allocation builds those two base channels first, then benefits from extra rearrangement capacity.

## Verification and limitations

Implementation and exact Fraction regression: `tools/arc_peonia_slot_frontier.py`. It enumerates every legal copy-count split for each of 15 tech budgets, checks every candidate is no larger than the recorded optimum, verifies Arc/Peonia symmetry, and checks the K=6 versus K=7 arranger threshold. It calls the `with_top_five` exact population model, itself validated against exhaustive labeled physical setups in the underlying result.

This is a **mathematical optimization of a deliberately narrow raw-access objective**, not a recommended competitive deck. The large K plans consume up to 16 deck slots on this one line and neglect attack setup, draw/search access, Supporter contention with other effects, locks, opponent interaction, discard/resource preservation, and card-in-hand already being sufficient without Peonia. F is optimistically expendable, and the same top-five effect class abstracts meaningful differences between Rotom Phone's shuffle and Pokédex's ordering outside the immediate target-placement action.

Practical next step: replace the single-event objective with conditional game-state value and explicit alternative uses of each connector, especially the Peonia Supporter opportunity cost.
