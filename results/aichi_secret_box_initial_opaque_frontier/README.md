# Initial Secret Box opaque-discard frontier

This result isolates the mandatory three-card Secret Box payment in the paired
Aichi Vileplume first-turn experiment.

For every Secret-Box-only success, the solver minimizes how many cards from the
existing compressed `other` category must be included in Secret Box's own
three-card discard. Later actions use the published Boolean continuation
planner and do not add cost to this metric.

The same 500,000 paired states with seed `20261007` contain 20,785 incremental
Secret Box successes. Every incremental state has an initial-payment witness.

| Minimum `other` cards in Secret Box payment | States | Share |
| ---: | ---: | ---: |
| 0 | 570 | 2.742362% |
| 1 | 4,598 | 22.121722% |
| 2 | 9,592 | 46.148665% |
| 3 | 6,025 | 28.987250% |

Cumulatively:

| Maximum allowed | States retained | Gain retained |
| ---: | ---: | ---: |
| 0 | 570 | 2.742362% |
| 1 | 5,168 | 24.864085% |
| 2 | 14,760 | 71.012750% |
| 3 | 20,785 | 100.000000% |

GitHub Actions run `37587405908` passed.

The distinction from
`results/aichi_secret_box_opaque_discard_frontier/` is timing. That result
counts opaque-category cards used by all represented discard payments. This
result counts only Secret Box's mandatory first payment.

The first-payment frontier is modestly less restrictive. A two-card opaque
limit retains 71.01% of the incremental states at the moment Secret Box is
played, compared with 66.56% when the entire represented sequence is scored.

This result still does not distinguish exact card names inside `other`.
Its next useful extension is a multi-objective or provenance-aware payment
model that preserves both initial-payment quality and total continuation cost.

Implementation:
- `tools/aichi_secret_box_initial_opaque_frontier.py`
- `results/aichi_secret_box_initial_opaque_frontier/reproduce.py`
