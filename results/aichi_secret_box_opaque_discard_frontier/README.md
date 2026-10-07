# Aichi Secret Box opaque-discard frontier

A cost-augmented version of the existing Aichi Secret Box planner measures the
minimum number of cards from its compressed `other` hand category used for
discard payments while preserving the first-turn core endpoint.

The paired 500,000-state run with seed `20261007` exactly reproduced the prior
353,262 Grand Tree successes, 374,047 Secret Box successes, 20,785 incremental
successes, and zero baseline-only successes.

Minimum `other` counts among incremental successes:

| Count | States | Share |
| ---: | ---: | ---: |
| 0 | 359 | 1.727207% |
| 1 | 3,868 | 18.609574% |
| 2 | 9,607 | 46.220832% |
| 3 | 6,714 | 32.302141% |
| 4 | 237 | 1.140245% |

Cumulatively, a limit of two retains 13,834 incremental states, or 66.557614%
of the unrestricted gain. A limit of three retains 20,548 states, or
98.859755%. The unrestricted first-turn gain is +4.1570 percentage points.

The cost solver matched the original Boolean planner on 20,000 validation
states with zero reachability mismatches. GitHub Actions run
`37586623671` passed.

The `other` category contains cards with different future roles, so this is a
representation-level preservation frontier. It does not assign card-specific
strategic value.

This result complements `results/temporal_discard_replenishment/`. That work
showed that later Guzma & Hala payments can be funded by cards generated after
Secret Box. The next useful refinement is therefore a provenance split between
pre-Box and generated `other` material.

Implementation:
- `tools/aichi_secret_box_opaque_discard_frontier.py`
- `results/aichi_secret_box_opaque_discard_frontier/reproduce.py`
