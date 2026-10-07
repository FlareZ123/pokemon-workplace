# Aichi Secret Box opaque Pareto frontier

This result jointly scores successful first-turn continuations by:

`(other cards in Secret Box's first payment, other cards used by all modeled payments)`

The paired 500,000-state run contains 20,785 Secret-Box-only successes. Every
state has exactly one nondominated cost pair, and there are zero tradeoff
states between minimizing the first-payment metric and minimizing the total
metric.

| Cost pair | States |
| --- | ---: |
| (2, 2) | 8,666 |
| (3, 3) | 5,788 |
| (1, 1) | 3,657 |
| (1, 2) | 941 |
| (2, 3) | 926 |
| (0, 0) | 359 |
| (3, 4) | 237 |
| (0, 1) | 211 |

In 18,470 states, 88.862160% of the incremental successes, both costs are
equal. In the remaining 2,315 states, 11.137840%, the total minimum is exactly
one card higher than the first-payment minimum.

The Pareto minima match both independently implemented scalar solvers on
10,000 validation states with zero mismatches. GitHub Actions run
`37588021062` passed.

The `other` bucket is still a compressed representation, so the result does
not assign value to individual card names. The next extension should preserve
exact card identities or strategic roles inside the feasible payment family.

Implementation:
- `tools/aichi_secret_box_opaque_pareto.py`
- `results/aichi_secret_box_opaque_pareto/reproduce.py`
