# Aichi Secret Box exact payment families

This result expands the initial Secret Box payment from the compressed
`other` category back to exact card names while keeping the same downstream
first-turn core semantics.

For each Secret-Box-only success in the seeded 100,000-state prefix, the solver
keeps every distinct three-card name multiset that can pay Secret Box and still
reach the Bunnelby + TM: Evolution + Jet Energy endpoint.

There are 4,175 incremental states and no missing payment families.

## Family geometry

The 4,175 states contain 80,912 feasible payment options in total, an average
of 19.380120 per state. Family sizes range from 4 to 70.

The minimum number of one-copy deck cards appearing in any feasible payment is:

| Singleton floor | States | Share |
| ---: | ---: | ---: |
| 0 | 3,577 | 85.676647% |
| 1 | 498 | 11.928144% |
| 2 | 90 | 2.155689% |
| 3 | 10 | 0.239521% |

Thus 598 states, 14.323353%, cannot preserve every singleton simultaneously.
Even so, no particular singleton card name appears in every feasible payment
in any sampled state.

This is a concrete example of set-valued discard pressure. A state can require
using at least one scarce card while still offering several different scarce
cards that can fill that role.

## Name-level protection cuts

For each payment family, the name-level protection cut is the minimum number of
card names that would have to become unavailable for every payment option to be
blocked.

| Cut size | States |
| ---: | ---: |
| 1 | 1 |
| 2 | 120 |
| 3 | 1,008 |
| 4 | 2,752 |
| 5 | 294 |

The mean cut is 3.770778 card names.

This shows why family geometry contains information that a scalar
discardability count cannot preserve. Most states require several distinct
card-name protections before every legal three-card payment disappears.

## Scope

The first part of the line is replayed with exact card names. Once Secret Box
resolves, the experiment returns to the existing compressed Aichi continuation
planner. Search choices inside categories that the older planner treats as
interchangeable are enumerated when they can affect the pre-Box hand.

The analysis still optimizes only the first-turn core endpoint. It does not
score later board value or matchup-specific continuation value.

GitHub Actions run `37588650999` passed.

Implementation:
- `tools/aichi_secret_box_payment_families.py`
- `results/aichi_secret_box_payment_families/reproduce.py`
