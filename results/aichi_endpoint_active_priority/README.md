# Aichi endpoint-aware starting-Active priority

A fixed setup-valid Active priority was developed on seed 20261007 and tested on 50,000 accepted openings with independent seed 20261008. The policy uses only opening Basic identities plus a preselected endpoint.

| Endpoint | Comparable | Existing mean pairs | Priority mean | Full-state ceiling |
| --- | ---: | ---: | ---: | ---: |
| core | 14,897 | 13.67410 | 13.94415 | 14.06176 |
| Pidgeot | 13,187 | 13.10237 | 13.84265 | 13.99348 |
| Stoutland | 10,760 | 13.00920 | 13.77835 | 13.93271 |
| dual Stage 2 | 9,389 | 12.78390 | 13.43828 | 13.68847 |
| Item lock | 10,094 | 11.19507 | 13.38686 | 13.80919 |
| Item + Pidgeot | 7,289 | 10.90122 | 12.38332 | 12.68020 |
| Item + Stoutland | 5,888 | 10.84256 | 12.32762 | 12.63179 |

The policy improves mean payment-pair count for every endpoint on the holdout. It is not statewise dominant and can be worse than the existing heuristic in a small minority of states.

Oddish is preferred for Item-lock endpoints because Fan Rotom cannot search it. Fan Rotom is preferred for the dual Colorless-evolution endpoint because Fan Call can cover Bunnelby, Pidgey, and Lillipup.

The full-state maximum is only a ceiling because it can use information unavailable when the starting Active is chosen.

Reproduction: `tools/aichi_endpoint_active_priority.py`, 50,000 trials, seed 20261008.
