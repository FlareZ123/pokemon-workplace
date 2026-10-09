# Exact likelihood theorem for two different random hand discards

## Result

The cancellation found in [the sequential hidden-Prize discard experiment](../prize_acquired_random_discard_chain/) is one case of a general combinatorial law.

Consider a hand containing a known `a` copies of card group A, a known `b` copies of group B, and one distinguished card of privately unknown group A or B. Two distinct hand cards are selected uniformly at random, one after the other without replacement. The public observes the groups **A then B**, or symmetrically **B then A**.

Implementation: `tools/mixed_random_discard_likelihood.py`  
Regression: `results/mixed_random_discard_likelihood/reproduce.py`

## Formula and proof

Write N=a+b+1. The likelihood of the observed ordered mixed pair is

- tagged card A: `L_A = (a+1)b/[N(N-1)]`;
- tagged card B: `L_B = a(b+1)/[N(N-1)]`.

Reversing the two public group observations yields the same likelihood. For positive a,b, the likelihood ratio `L_A/L_B = (a+1)b/[a(b+1)]`. Its comparison with one has the sign of `b-a`.

Consequently:

- **a=b:** the ratio is exactly one. The mixed-pair observation does not update any prior probability of the tagged card's class. It cannot update another variable correlated with the tagged class through that channel either.
- **a less than b:** the mixed pair favors tagged group A (fewer known A copies).
- **a greater than b:** it favors tagged group B (fewer known B copies).

With `a=0` or `b=0`, the observed mixed pair can identify which group the tagged card must belong to. A degenerate impossible observation is rejected.

For prior `p=P(tag A)`, the posterior is `pL_A/[pL_A+(1-p)L_B]`. Conditional on the ordered mixed pair, the tagged physical card's survival probability is `a/(a+1)` if tagged A and `b/(b+1)` if tagged B. Their posterior-weighted average is the total survival probability.

## Illustrative exact results

Using p=2/7:

| Known A copies | Known B copies | Posterior P(tag A) | P(tag remains) |
| ---: | ---: | ---: | ---: |
| 1 | 1 | 2/7 | 1/2 |
| 2 | 1 | 3/13 | 7/13 |
| 1 | 2 | 8/23 | 14/23 |
| 0 | 2 | 1 | 0 |
| 2 | 0 | 0 | 0 |

## Independent verification

The reproducer enumerates ordered *physical index pairs* from every hand with a and b each between 0 and 5, across five prior tag-class probabilities. It checks the exact Fraction-valued public-group likelihood and the probability the tagged card remains unselected. Both public mixed orders are verified. It also tests cancellation for every equal count 1 through 5 and both asymmetric examples above.

## Strategic and modeling relevance

This theorem formalizes when observing a second random discard restores an opponent's former hidden-card belief, and when that cancellation fails due to asymmetric known hand composition. It is valid under uniform sampling without replacement and the stated known-hand multiset. It is mathematically reusable for a previously Prized card, searched hidden hand cards, or any other physically distinguished card whose group is private.

Real Pokémon TCG random-discard effects need their own legality and timing checks. The bundled Expanded-legal Mars `sm5-128` is one example of a relevant random opponent-hand discard action; it supplies one random discard only after its antecedent draw succeeds.
