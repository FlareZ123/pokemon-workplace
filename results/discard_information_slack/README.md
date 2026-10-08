# Discard-information slack boundary

This result identifies when hidden replacement information can change a discard-before-search payment.

Implementation: `tools/discard_information_slack.py`  
Regression: `reproduce.py`

Let:

- `d` = discard cost;
- `s` = visible cards that are safe to discard in every hidden world relevant to the endpoint;
- `m` = critical discard candidates whose safety depends on hidden replacements.

The payment is forced to consume

`q = max(0, d - s)`

critical candidates.

Under the symmetric one-replacement-per-critical-class model:

- `q = 0`: a fixed safe payment exists, so payment-choice information has zero value;
- `0 < q < m`: some critical cards must be discarded and a choice remains, so hidden information can change the best action;
- `q = m`: every critical candidate is forced, so information cannot change the selection.

For `U=52` unseen cards, `P=6` Prizes, `m=2`, and `q=1`, the exact benchmark is:

| Policy | Success |
| --- | ---: |
| Fixed K0 | 88.461538% |
| Informed | 98.868778% |
| Gap | 10.407240 pp |

This reproduces the earlier local Secret Box counterexample.

For direct Guzma & Hala in the richest modeled Aichi endpoint, six cards remain after the Active and played Supporter leave the hand. When the paid branch is needed, at most four visible cards must be preserved, leaving at least two always-safe cards for the two-card cost. Therefore `q=0`, predicting the zero K0/oracle gap independently confirmed by `results/aichi_gnh_k0_policy/`.

The boundary is local to the payment decision. Hidden information may still matter for target availability, timing, later connector contention, or longer-horizon card value.
