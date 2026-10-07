# Aichi discard-family robustness

## Question

Raw feasible-pair count measures current discard flexibility. This result asks
how easily that flexibility collapses when additional cards become protected or
effectively UDP.

For each successful Guzma & Hala discard family, define the **name-protection
cut** as the smallest set of card names that intersects every feasible payment.
Protecting all names in such a set makes the modeled discard cost unpayable.

A larger minimum cut means the payment family is structurally harder to destroy.

## Method

The sample and endpoint logic match the Aichi starting-Active discard-flexibility
audit:

- 100,000 accepted openings;
- seed 20261007;
- Jirachi absent;
- Bunnelby plus another Basic in the opening;
- existing Active policy compared with Jirachi-first/Bunnelby-first;
- only states where both policies use a successful Guzma & Hala route for the
  same endpoint.

The cut is computed over card names because the current ALS discard enumerator
also records feasible payments at card-name level.

## Results

| Endpoint | Comparable states | Existing mean cut | Bunnelby-first mean cut | B-first larger | Existing larger |
| --- | ---: | ---: | ---: | ---: | ---: |
| core | 10,343 | 4.61278 | 4.76912 | 1,934 | 317 |
| Pidgeot | 9,586 | 4.51575 | 4.73086 | 2,500 | 438 |
| Stoutland | 7,947 | 4.49063 | 4.71159 | 2,125 | 369 |
| dual Stage 2 | 6,936 | 4.47636 | 4.50043 | 1,070 | 903 |
| Item lock | 9,578 | 4.01107 | 4.72614 | 7,089 | 240 |
| Item lock + Pidgeot | 5,384 | 3.99777 | 3.83042 | 728 | 1,629 |
| Item lock + Stoutland | 4,484 | 3.97391 | 3.81111 | 639 | 1,369 |

For Item lock alone, Bunnelby-first increases the mean cut by 0.71507 names,
about 17.83%, and has the larger cut in 74.01% of comparable states. The
existing policy has the larger cut in only 2.51%.

For Item lock + Pidgeot, Bunnelby-first lowers the mean cut by 0.16735 names.
The existing policy has the larger cut in 30.26% of comparable states, compared
with 13.52% for Bunnelby-first.

For Item lock + Stoutland, Bunnelby-first lowers the mean cut by 0.16280 names.
The existing policy has the larger cut in 30.53% of comparable states, compared
with 14.25% for Bunnelby-first.

## Distribution detail

Item lock under the existing policy has cut-size counts:

- cut 1: 1
- cut 2: 97
- cut 3: 1,332
- cut 4: 6,513
- cut 5: 1,635

Item lock under Bunnelby-first shifts strongly upward:

- cut 2: 8
- cut 3: 193
- cut 4: 2,213
- cut 5: 7,164

The combined Item-lock endpoints show a different shape. For Item + Pidgeot,
Bunnelby-first concentrates 4,486 of 5,384 comparable states at cut 4 and only
22 at cut 5, while the existing policy reaches cut 5 in 1,321 states.

## Interpretation

This result strengthens the earlier feasible-pair-count finding. Starting Active
changes the topology of the available discard family even when immediate
endpoint reachability is identical.

Item lock alone benefits strongly from protecting Bunnelby in the Active Spot.
The combined endpoints require additional evolution Basics, so protecting a
different opening Basic can preserve more mutually substitutable discard
options.

The minimum cut supplies a robustness quantity that pair count cannot recover.
The generic counterexample in results/discard_feasibility_hypergraph/ shows why:
families can share option count and per-card marginals while having different
minimum cuts.

## Limitations

The cut treats protection by card name. A physical-copy model could distinguish
two copies of the same name and may change some cuts.

Every protected name is weighted equally. Matchup-dependent DCI can make one
protection event far more strategically plausible or important than another.

The measure is a local robustness property. It does not propagate surviving
payments into later-turn continuation value.

## Reproduction

- tool: tools/aichi_discard_family_robustness.py
- workflow: .github/workflows/validate-aichi-discard-family-robustness.yml
- trials: 100,000
- seed: 20261007
- CI run: 37585240816
