# The decision value of seeing a searched Pokémon's exact print

## Question

When a searched Pokémon's specific printing carries extra information about hidden Prize cards, how much can that information improve the opponent's subsequent choice?

The answer depends on the opponent's action payoffs. For a controlled two-action Prize-status guessing game, exact print information yields a **1/14 (7.142857 percentage-point)** improvement in probability of making the correct choice. Under a different utility function the same print observation can have **zero** decision value, even though it still contains positive Shannon information.

## Evidence base

The underlying public-observation probabilities come from [revealed_print_information](../revealed_print_information/) and use two legal, attack-distinct Pikachu prints from the bundled Expanded pool, `xy1-42` and `swsh7-49`.

A six-card toy pool has critical singleton A, two distinct Pikachu printings, and three fillers. Two Prize slots are uniform, followed by a K1-informed choice of which available Pikachu to reveal and a shuffled top card. Of 15 equally probable unordered Prize placements, seven choose each print, and one cannot choose either print. This experiment conditions on the 14 successful-search states.

After seeing only the common name, the opponent has P(A Prized)=5/14. Knowing the older print changes this to 4/7; knowing the newer print changes it to 1/7. Each print occurs with conditional probability 1/2.

## Exact policy evaluation

Suppose the opponent can choose either `assume_prized` or `assume_unprized`. Each correctly chosen binary status earns one utility unit; an incorrect choice earns zero.

| Information | Optimal choice | Expected correct choice |
| --- | --- | ---: |
| Name only, Pikachu | Assume unprized | 9/14 = 64.285714% |
| Old print `xy1-42` | Assume Prized | 4/7 = 57.142857% conditional on old |
| New print `swsh7-49` | Assume unprized | 6/7 = 85.714286% conditional on new |
| Both print outcomes, averaged | Print-dependent choice | 5/7 = 71.428571% |

The value of exact-print information is `5/7 - 9/14 = 1/14`, an improvement of 7.142857 percentage points.

This example demonstrates a **policy reversal** in the response to a print observation. The result is a mathematical property of the specified toy decision problem and search policy, not an actual TCG match win-rate estimate.

## Information is not equivalent to decision value

Keep the source probabilities and search choice policy unchanged, but pay only one-quarter of a utility unit for correctly guessing that A is Prized, while correctly guessing that it is unprized still pays one unit. The threshold for selecting the Prized action rises above both print-conditional posteriors. Then `assume_unprized` remains optimal for both print observations and the name observation, and the additional print evidence has exactly **zero** value for this decision.

Conversely, pay two utility units for correctly identifying A as Prized and one for correctly identifying it as unprized. The name-only player chooses Prized, whereas the print-aware player chooses Prized after the old print and unprized after the new print. The exact utility increases from 5/7 to 1, an information decision gain of **2/7**.

These contrasting payoff regimes are the relevant strategic principle: conditional information has practical value through the decisions it changes and the importance of the resulting outcomes.

## Method and reproducibility

- Exact observation/payoff engine: `tools/observation_policy_envelope.py`.
- Exact search/Pikachu print branch oracle: `tools/revealed_print_information.py`.
- Reproducer: `results/revealed_print_decision_value/reproduce.py`.
- Workflow: `.github/workflows/validate-revealed-print-decision-value.yml`.

The reproducer uses all 84 post-shuffle labeled states with `Fraction(1,84)` mass each, derives the optimal deterministic response conditional on the chosen observation channel, and independently brute-forces every feasible mapping from observation to action. It tests three payoff regimes and their exact expected utilities.

## Limits and next integration

The response actions are synthetic predictions with well-defined utility. A realistic model would replace them with available game actions, such as a gust, attack, Item lock, or targeted resource disruption, each evaluated under board position, remaining Prize count, accessible hand, Supporter usage, and matchup. Crucially, a card's revealed attack text may itself affect the best response, independently of any Bayesian inference.

Combining print-aware observations with actual legal-response evaluation could identify real states where the extra information materially changes play. The current example establishes the exact informational mechanism and its decision-value dependence.
