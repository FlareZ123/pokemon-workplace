# Agent7: Aichi Secret Box opaque-payment frontiers

I added two paired 500,000-state extensions to the existing Aichi Grand Tree -> Secret Box first-turn result.

## Total compressed-other frontier

`results/aichi_secret_box_opaque_discard_frontier/`

Among the 20,785 Secret-Box-only successes, the minimum number of cards from the planner's compressed `other` category used across represented discard payments is:

- 0: 359
- 1: 3,868
- 2: 9,607
- 3: 6,714
- 4: 237

A maximum of two retains 66.557614% of the gain; three retains 98.859755%.

## Initial Secret Box payment

`results/aichi_secret_box_initial_opaque_frontier/`

Counting only Secret Box's mandatory three-card payment:

- 0: 570
- 1: 4,598
- 2: 9,592
- 3: 6,025

A maximum of two retains 71.012750% of incremental states.

Both preserve the original 20,785 incremental count. The total-cost solver matched the prior Boolean reachability planner on 20,000 validation states with zero mismatches. CI runs 37586623671 and 37587557763 passed.

Interpretation: the immediate Secret Box gain usually requires some non-core hand material to remain usable for discard, while the extra pressure after the first payment is smaller. The `other` category is strategically heterogeneous, so these are representation-level preservation frontiers rather than card-specific DCI values.

The strongest next extension is provenance-aware multi-objective cost: preserve initial-payment quality and total continuation cost together rather than minimize each independently.
