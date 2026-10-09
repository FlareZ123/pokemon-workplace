# Deck-size scaling changes whether print choices identify an opponent's policy

## Question

In the six-card Pikachu toy, two opposite K1 target-choice policies select old and new Pikachu equally often, so repeated print observations alone never distinguish the policies.

Does that remain true in the more realistic 52-card unknown pool with six Prizes?

**No.** Under the same two policies and three singleton conditions, selected-print frequencies become strongly asymmetric. This allows the observer to learn the opponent's preferred choice pattern from publicly seen printings even without learning previous hidden Prize cards.

## The two unknown policies

The pool has U=52 cards, including singleton A, old print X (`xy1-42`), new print Y (`swsh7-49`), and 49 fillers; P=6 randomly Prized cards. The target choice is made after a full deck inspection and the search is known to succeed. The two possible persistent strategies are:

- **Forward:** prefer X when A is Prized, otherwise prefer Y when available, with X fallback.
- **Reverse:** the corresponding swapped-print preference, favoring Y when A is Prized and otherwise X with Y fallback.

Both are explicitly hypothetical. They appear in [latent_search_policy_information](../latent_search_policy_information/).

## Scale changes print frequencies

| Model | P(X chosen | forward, search success) | P(Y chosen | forward, search success) |
| --- | ---: | ---: |
| U=6, P=2 | 1/2 | 1/2 |
| **U=52, P=6** | **1/5** | **4/5** |

The reverse policy swaps the two frequencies in either model.

With equal initial policy priors, observing one Y in the 52-card model changes P(forward) from 1/2 to **4/5**. Another independent Y multiplies the odds by four again, leading to 16/17; a third leads to 64/65, and a fourth to 256/257.

In the six-card toy, either print has likelihood 1/2 under both policies, so the posterior never changes without additional evidence. The difference is created by physical Prize frequency and availability geometry.

## Print evidence versus hidden A

Under a 1/2-1/2 policy mixture in the 52-card pool, observing X or Y still yields the same **P(A Prized)=11/95**. The print alone does not inform A's status at this prior, even though it informs the searcher's policy.

As policy confidence changes, the print's interpretation changes. For the equal-reward binary choice "predict A Prized or unprized," the observer should reverse their ordinary unprized response after X only if their prior P(forward) exceeds the exact threshold:

`74/75 ≈ 98.6667%`.

The corresponding reversed threshold for a Y observation is P(forward) below 1/75.

### How many past unlabeled searches does it take?

Assume four separate past games each ended up publicly revealing Y, while the searcher used one persistent policy. The observer does not know those games' A Prize allocations.

| Past Y observations | P(forward) | Value of a print-specific response in the next game |
| ---: | ---: | ---: |
| 0 | 1/2 | 0 |
| 1 | 4/5 | 0 |
| 2 | 16/17 | 0 |
| 3 | 64/65 | 0 |
| 4 | 256/257 | **182/24415**, approximately 0.7454 percentage points |

Thus behavioral inference accumulates before an observed print becomes useful to the specified next-game binary decision. The threshold comes from the weak edge of X's 10/19 posterior over 1/2 even when the forward policy is certain, together with asymmetric print frequencies.

## Reusable exact model

`tools/expanded_policy_identifiability.py` composes the symbolic hypergeometric probabilities from `tools/expanded_singleton_reveal_hypergeometric.py` with exact Bayesian odds updates. It preserves the distinction between the policy posterior and Prize posterior conditional on a specific print.

The regression `results/expanded_policy_identifiability/reproduce.py` checks six-card non-identifiability, 52-card likelihood ratios, posterior odds after five sequential identical print choices, threshold crossings, alternative print symmetry, 101 rational prior points, and invalid evidence.

Workflow: `.github/workflows/validate-expanded-policy-identifiability.yml`.

## Interpretation and limitations

The 52-card unknown pool is conditional on A and both Pikachu printings being absent from the player's known eight-card hand, and every game is treated as an independent new Prize deal with that same conditional composition. The model uses synthetic target choices to expose the information mechanism; no real player's behavior is asserted.

Actual policy learning must account for opponent deck construction, available actions, changing metagame plans, the specific turn, Prize knowledge, and why a search was made. But the exact result illustrates an important interaction: physical card-population size can turn unidentifiable behavioral observations into signals about an opponent's persistent decision policy, even when those observations initially say nothing about the hidden card of interest.
