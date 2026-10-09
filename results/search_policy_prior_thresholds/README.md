# When confidence in an opponent's search policy makes a print reveal actionable

## Question

In the unknown-policy [latent search study](../latent_search_policy_information/), two opposite target-selection strategies were equally plausible. Their print-specific Prize signals canceled exactly. As the opponent becomes more confident in one policy, does the printing observation immediately improve their next decision?

The answer is conditional on the response payoff. Under equal-reward binary Prize-status prediction, **print identity has zero decision value over an unexpectedly wide range of opponent-policy priors, from 1/6 through 5/6 inclusive**, despite carrying positive Shannon information at most interior priors.

## Controlled model

Reuse six cards: singleton A, two distinct same-name Pikachu printings `xy1-42` and `swsh7-49`, and three fillers, two uniformly dealt Prizes, with a single selected target after full deck inspection.

The searching player's hidden policy is either *forward* (old print preferred when A is Prized) or *reverse* (new print preferred when A is Prized), as defined in [latent_search_policy_information](../latent_search_policy_information/).

Let `a` be the observer's prior probability of the forward policy, and `1-a` the reverse-policy probability. Each policy produces either printing in seven of fifteen initial Prize configurations, so seeing the print does not itself change their relative policy probability. All following probabilities condition on a successfully executed search.

## Posterior formulas

By direct combinatorial enumeration, observing old Pikachu yields:

`P(A Prized | old, a) = (1 + 3a) / 7`.

Observing new Pikachu yields:

`P(A Prized | new, a) = (4 - 3a) / 7`.

If the opponent records only the common name, the conditional probability is always `5/14`, independent of `a`. Both prints still occur with conditional probability 1/2.

For an opponent whose next decision is the abstract binary response "predict A Prized or unprized" with equal reward for being correct, name-only best expected accuracy is **9/14**.

The additional correct-prediction probability from print information has the exact piecewise form:

`V(a) = max(0, (6a-5)/14, (1-6a)/14)`.

Consequently:

- For `1/6 <= a <= 5/6`, both print-specific Prize posteriors are at most 1/2. The correct-response policy is unchanged, and `V(a)=0`.
- For `a > 5/6`, knowing the old print makes "Prized" the better response, yielding `V(a)=(6a-5)/14`.
- For `a < 1/6`, knowing the new print makes "Prized" the better response, yielding `V(a)=(1-6a)/14`.
- At `a=0` or `a=1`, the response benefit reaches **1/14**.

### Positive information with no immediate action improvement

At `a=3/4`, observing old Pikachu makes P(A Prized)=**13/28**, while observing new makes it **1/4**. The printing supplies **0.036488636662 bits** of mutual information about whether A is Prized. Both posteriors remain below 1/2, so a rational equal-reward binary predictor still chooses "unprized" either way. Exact action-value gain is **zero**.

This is a general instance of **decision sufficiency**: coarse observations can be adequate for a specific decision even when richer observations reduce uncertainty.

## Method

The model reuses `tools/latent_search_policy_belief.py`, which enumerates joint print/Prize/unknown-policy hypotheses with exact rational mass, and `tools/observation_policy_envelope.py`, which computes best observation-consistent responses.

The test `results/search_policy_prior_thresholds/reproduce.py` evaluates 61 rational priors `a=0/60, ..., 60/60`, independently checks both posterior formulas, both marginal print frequencies, the stable name-only payoff, the exact piecewise decision-gain formula, and threshold interior/boundary cases. A separate entropy regression checks the positive-information/zero-value example.

CI workflow: `.github/workflows/validate-search-policy-prior-thresholds.yml`.

## Interpretation and limitations

A Pokémon TCG opponent who knows the searched print may still fail to use that information for a particular strategic decision because their uncertainty about the searcher's behavioral policy is too great to change the optimal response. The threshold values here come from a deliberately symmetric toy with equal correct-choice rewards. They are mathematical benchmarks and cannot be imported as opponent-confidence thresholds for real Expanded matchups.

For realistic modeling, substitute measured or strategically derived search-policy likelihoods and responses whose payoffs reflect actual board states, cards in hand, attacks, disruption channels, and Prize values. Compare such policies under K0/K1 timing, finite-copy uncertainty, and matchups rather than applying the toy threshold universally.
