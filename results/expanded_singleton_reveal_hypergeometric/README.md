# Exact print-reveal Prize inference on a 60-card-like hidden pool

## Question

The earlier print-reveal signal used only six hidden cards. Does the same mechanism survive when the uncertainty represents a real 60-card Expanded deck, with six Prizes and the cards already drawn into hand?

Yes, under a conditional 52-card unknown pool and the same synthetic, precisely specified K1 search preference. The signal remains strong in the less-common revealed printing, while its overall decision value becomes smaller than in the toy due to the singleton's low prior Prize probability.

## Setup and rules boundary

A player has a 60-card deck and eight known cards outside their hidden deck-plus-Prize pool, such as seven opening cards plus one subsequent draw. Of the remaining **52 cards**, six are randomly set as face-down Prizes and 46 remain in deck. Assume, as a condition of the experiment, that the three distinguished singleton cards are all in this unknown pool:

- important singleton A;
- old Pikachu printing X, `xy1-42`;
- new Pikachu printing Y, `swsh7-49`.

The remaining 49 cards are treated as filler. The printed Basic Pokémon are both eligible for a Quick Ball-style Basic search. The search is assumed to be the first full deck inspection, giving the actor K1 Prize composition before choosing its target; any discard payment required before search is held fixed and outside the modeled pool.

The synthetic target-choice policy is the same as the six-card study: take X when A is Prized and X is available; otherwise take Y if available, otherwise X if available, otherwise fail when both target printings are Prized.

This is a **conditional search event**, without a claim that a specific tournament deck would actually include both Pikachu prints or follow this policy. It does respect a 60-card/6-Prize population geometry.

## Exact 52-card benchmark

| Event or belief | Exact | Probability |
| --- | ---: | ---: |
| A target printing is accessible | 437/442 | 98.868778% |
| Search reveals X, conditional on success | 1/5 | 20.000000% |
| Search reveals Y, conditional on success | 4/5 | 80.000000% |
| A Prized, after only knowing a Pikachu search succeeded | 11/95 | 11.578947% |
| A Prized after X revealed | **10/19** | **52.631579%** |
| A Prized after Y revealed | **1/76** | **1.315789%** |

For the controlled equal-reward decision to predict A's Prize status, a name-only observer gets 84/95 = 88.421053% correct. Knowing which print was revealed yields 17/19 = 89.473684% correct, an exact gain of **1/95 = 1.052632 percentage points**.

Thus the rarity and severity of a decisive conditional cue can diverge: a selected print used only 20% of successful searches more than quadruples the conditional belief that A is Prized, but the average binary decision improvement is about one percentage point under this endpoint.

## Finite-population theorem

More generally, let:

- `U` be the unknown deck-plus-Prize pool size;
- `P` be the number of uniformly random face-down Prizes;
- three named distinguished singletons A, X, Y all belong to that unknown pool;
- the above deterministic search choice is applied after full deck inspection.

Under nondegenerate `2 <= P <= U-2`, the probability that X is revealed changes A's posterior to

`P(A Prized | X) = (U-2)/(2U-P-3)`.

For every `P>1`, this is **strictly greater than 1/2**, regardless of how large the unknown pool is. The corresponding Y-reveal posterior is

`P(A Prized | Y) = P(P-1) / [P(P-1) + (U-2)(U-P-1)]`.

The probability of a successful search is

`1 - P(P-1)/[U(U-1)]`,

because failure requires both possible targets to be Prized.

When `2 <= P < U/2`, the optimal equal-reward name-only response predicts A unprized, the print-aware response predicts Prized after X, and the Y observation leaves the unprized prediction optimal. The exact increase in correct-decision probability is

`P(P-1)(U-P) / [(U-2)(U(U-1)-P(P-1))]`.

These formulas come directly from hypergeometric probabilities for membership of A/X/Y among the Prize cards. They are fully conditional on the specified behavioral selection policy.

## Validation

Implementation: `tools/expanded_singleton_reveal_hypergeometric.py` offers two independent exact `Fraction` algorithms: eight possible singleton-Prize membership states and separately derived symbolic expressions.

Regression: `results/expanded_singleton_reveal_hypergeometric/reproduce.py`.

The test compares both implementations for all pool sizes `U=5..65` and every admissible `P`, totaling **1,952** scenarios. For `U<=9` it adds a completely independent physical Prize-subset enumeration over all combinations. It verifies the original six-card posterior, all 52-card benchmark fractions, and the decision-gain theorem over the low-Prize region.

CI: `.github/workflows/validate-expanded-singleton-reveal-hypergeometric.yml`.

## Scope and strategic significance

The card-choice policy is intentionally invented to test what a known K1-dependent choice can reveal about hidden Prize status. A rational player might prefer an unrelated card in these same physical worlds; real opponents may have uncertainty over the policy, as shown in [latent_search_policy_information](../latent_search_policy_information/). The result is therefore an exact **conditional information and decision model**, not an estimate of real Expanded match success.

It nevertheless demonstrates that the print-level information effect is compatible with real deck and Prize counts. A rare but highly diagnostic observed search target can be worth modeling even if the overall information effect averages to a modest gain. The next step is to choose a real archetype, actual search targets, and payoff-relevant alternative lines.
