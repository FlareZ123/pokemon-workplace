# Aichi Active choice: forced singleton discards

This result extends the starting-Active discard-flexibility audit by asking
whether a successful Guzma & Hala route forces one specific one-copy card name.

## Method

The 100,000-state sample is restricted to openings where Jirachi is absent,
Bunnelby is present, another Basic is present, and the two legal Active
heuristics differ. For each endpoint and policy, every endpoint-preserving
two-card Guzma & Hala discard pair is enumerated.

A singleton name is "forced" when it appears in every feasible pair.

## Findings

| Endpoint | Comparable G&H states | Existing forced-name states | Bunnelby-first forced-name states |
| --- | ---: | ---: | ---: |
| core | 10,343 | 0 | 0 |
| Pidgeot | 9,586 | 0 | 0 |
| Stoutland | 7,947 | 0 | 0 |
| dual Stage 2 | 6,936 | 0 | 0 |
| Item lock | 9,578 | 0 | 0 |
| Item lock + Pidgeot | 5,384 | 1 | 0 |
| Item lock + Stoutland | 4,484 | 0 | 0 |

The single forced-name state under the existing Item-lock-plus-Pidgeot policy
had both Budew and Mr. Mime in every feasible pair. Everywhere else, even when
at least one singleton had to be discarded, the player retained a choice among
scarce names.

The policies also differ in whether an all-non-singleton pair exists. In
comparable states, Bunnelby-first restored such a pair 225 times for Item lock
while the existing policy restored it 85 times. For Item lock + Pidgeot the
counts reversed to 38 versus 180, and for Item lock + Stoutland to 30 versus
124.

## Interpretation

The useful discard object is a family of jointly feasible pairs. Pair count,
minimum singleton count, forced-name intersection, and later continuation value
measure different properties of that family.

This gives concrete evidence for treating scalar DCI as an approximation. A
card can be individually undesirable to discard while the hand still contains
several alternative scarce-card pairs, so no particular card is forced.

## Reproduction

- tool: tools/aichi_active_forced_singletons.py
- workflow: .github/workflows/validate-aichi-active-forced-singletons.yml
- trials: 100,000
- seed: 20261007
- CI run: 37584693885
