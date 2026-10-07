# Aichi physical-copy discard robustness

## Purpose

The name-level robustness audit treats all copies of a card name as one
protection target. This refinement expands each endpoint-preserving Guzma &
Hala payment into physical hand-copy vertices before computing the minimum
protection cut.

The physical cut is the smallest number of individual cards that would have to
become protected before every modeled payment is blocked.

## Method

The sample matches the other starting-Active discard studies:

- 100,000 accepted openings;
- seed 20261007;
- Jirachi absent;
- Bunnelby plus another Basic present;
- both Active policies have a successful G&H route for the same endpoint.

A feasible name pair is expanded across all physical copies currently in the
discard pool. For example, if a feasible payment is X + Y with two X copies and
three Y copies, it becomes six physical edges.

## Results

| Endpoint | Comparable | Existing mean physical cut | Bunnelby-first mean | B-first larger | Existing larger |
| --- | ---: | ---: | ---: | ---: | ---: |
| core | 10,343 | 4.75694 | 4.94914 | 1,988 | 0 |
| Pidgeot | 9,586 | 4.63165 | 4.87075 | 2,573 | 281 |
| Stoutland | 7,947 | 4.62237 | 4.86611 | 2,166 | 229 |
| dual Stage 2 | 6,936 | 4.58391 | 4.61952 | 1,079 | 832 |
| Item lock | 9,578 | 4.12946 | 4.86834 | 7,310 | 233 |
| Item lock + Pidgeot | 5,384 | 4.08377 | 3.92013 | 738 | 1,619 |
| Item lock + Stoutland | 4,484 | 4.07605 | 3.91659 | 641 | 1,356 |

The physical-copy model therefore preserves the earlier direction.

For Item lock, Bunnelby-first increases mean cut by 0.73888 cards, about
17.89%. It has the larger cut in 76.32% of comparable states; the existing
policy has the larger cut in 2.43%.

For Item lock + Pidgeot, the existing policy has the larger cut in 30.07% of
states, compared with 13.71% for Bunnelby-first. Mean cut moves from 4.08377
to 3.92013 under Bunnelby-first.

For Item lock + Stoutland, the existing policy has the larger cut in 30.24% of
states, compared with 14.30% for Bunnelby-first. Mean cut moves from 4.07605
to 3.91659.

The core endpoint is especially clean in this sample: Bunnelby-first has an
equal or larger physical cut in every one of the 10,343 comparable states. It
is strictly larger in 1,988 and equal in 8,355.

## Interpretation

The Active-choice tradeoff survives a more faithful treatment of duplicate
cards.

The simple endpoints usually gain discard robustness when Bunnelby occupies the
Active Spot. Combined Item-lock endpoints often benefit from using the Active
position to protect an additional required evolution Basic instead.

The physical cut and the name cut answer different questions:

- name cut measures how many card categories must become globally protected;
- physical cut measures how many actual cards in this hand must become
  unavailable as discard material.

Both support the same endpoint-dependent strategic conclusion in this sample.

## Limitations

Physical cards with the same name still share the same strategic value model.
A future continuation layer can distinguish copies indirectly through attached
state, Prize information, recovery plans, or later sequencing.

The protection cut weights every newly UDP card equally and does not assign
matchup-dependent probabilities to protection events.

## Reproduction

- tool: tools/aichi_physical_discard_robustness.py
- workflow: .github/workflows/validate-aichi-physical-discard-robustness.yml
- trials: 100,000
- seed: 20261007
- CI run: 37585593248
