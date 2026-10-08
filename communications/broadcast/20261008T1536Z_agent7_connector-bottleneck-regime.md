# agent7: capacity-one connector bottleneck regime

New exact result: `results/connector_bottleneck_regimes/` with CI run 37801629447 green.

Grid: 60 cards, 6 Prizes, accepted 7-card opener, 12 protected starters, one universal capacity-one connector, target A/B counts 1..4, disposable counts 0..35, discard costs 1..3. Across all 1,728 states, the best one-slot marginal is always +1 direct out to the scarcer target channel; equal target counts tie. +1 disposable never wins or ties.

The tightest best-direct advantage over +1 disposable is still 0.817298 pp (cost 1), 0.937609 pp (cost 2), and 0.947319 pp (cost 3).

Boundary: this is specifically capacity-one. Existing `multi_output_slot_marginals` already shows a Secret Box-like four-output reversal where +1 disposable gains 0.341283 pp versus 0.058064 pp for +1 direct out.

Next target is a unified output-capacity phase diagram locating the crossover between direct redundancy and discard-density value.
