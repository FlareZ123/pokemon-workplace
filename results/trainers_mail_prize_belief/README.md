# Prize information from repeated Trainers' Mail misses

## Question

How much does repeatedly missing a singleton with Trainers' Mail change the belief that the card is in the Prize cards, and can those partial observations make Gladion preferable to Guzma & Hala before a full deck search?

This result isolates the information channel created by top-four inspection.

Implementation: `tools/trainers_mail_prize_belief.py`  
Regression: `results/trainers_mail_prize_belief/reproduce.py`

## Stylized decision state

Assume:

- the first turn going second has reached the normal draw;
- one required singleton is absent from the player's known cards;
- six Prize cards remain face down;
- 46 cards remain in the deck;
- the only uncertainty relevant to the decision is whether the singleton is in the six Prizes or the 46-card deck;
- Guzma & Hala succeeds if the singleton is in the deck;
- Gladion succeeds if the singleton is Prized;
- both Supporters are otherwise available.

Before any additional observation, the singleton is uniformly located among 52 unknown physical positions.

Therefore:

- `P(Prized) = 6 / 52 = 11.538461538%`;
- `P(deck) = 46 / 52 = 88.461538462%`.

The model then conditions on Trainers' Mail looking at four cards and failing to reveal the singleton. The four cards are returned to the same-size deck before the next modeled Mail, so repeated misses are independent conditional on the singleton being in the deck.

## Exact posterior sequence

| Consecutive Mail misses | P(singleton Prized) | P(singleton in deck) |
| ---: | ---: | ---: |
| 0 | 11.538461538% | 88.461538462% |
| 1 | 12.500000000% | 87.500000000% |
| 2 | 13.529411765% | 86.470588235% |
| 3 | 14.629424779% | 85.370575221% |
| 4 | 15.802530067% | 84.197469933% |

For one miss, the update is especially simple. If the singleton is in the deck, Trainers' Mail misses it with probability `42/46`. If it is Prized, the Mail necessarily misses it.

Bayes' rule gives:

`P(Prized | miss) = 6 / (6 + 46 * 42/46) = 6/48 = 1/8`.

For `k` misses:

`P(Prized | k misses) = 6 / (6 + 46 * (42/46)^k)`.

## Finding 1: four Mail misses do not make blind Gladion preferable

In the binary reachability abstraction:

- Guzma & Hala has success probability `P(deck)`;
- Gladion has success probability `P(Prized)`.

Gladion becomes the better fixed choice only when the Prize posterior exceeds 50%.

Four consecutive misses raise the Prize posterior only to **15.802530067%**.

Under the fixed-size repeated-look model, the posterior first exceeds 50% after **23 consecutive misses**.

The published Aichi Iron Thorns lists contain at most four Trainers' Mail, so partial Mail misses alone do not approach the action-switch threshold in this stylized state.

This supports an observation-only policy that still prioritizes Guzma & Hala over a blind Gladion after ordinary Mail misses.

## Finding 2: full-deck inspection is qualitatively stronger than repeated partial misses

Tag Call performs a full deck search. After that inspection, a skilled player who knows the decklist can infer whether the singleton is Prized.

The posterior therefore collapses to either:

- 0% Prized, if the singleton is in the deck; or
- 100% Prized, if it is absent from the deck and known elsewhere not to be.

That can justify a precise Guzma & Hala versus Gladion pivot.

Trainers' Mail supplies partial negative evidence instead. Even several misses leave the deck state overwhelmingly more likely.

The two search effects should therefore not share one generic "looked at deck" information flag.

## Finding 3: negative partial evidence can increase the value of exact information

Before any Mail miss, the best fixed Supporter succeeds with probability 88.461538462%.

If exact location were learned before choosing, the correct Supporter could be selected in either state, giving 100% success inside this binary abstraction.

The decision value of exact information is therefore the smaller posterior mass:

`V_exact - V_fixed = min(P(Prized), P(deck))`.

That value rises as repeated Mail misses move the posterior toward 50%:

| Mail misses | Value of exact location information |
| ---: | ---: |
| 0 | 11.538461538 pp |
| 1 | 12.500000000 pp |
| 2 | 13.529411765 pp |
| 3 | 14.629424779 pp |
| 4 | 15.802530067 pp |

The partial observation reduces uncertainty about some aspects of the deck while making the unresolved deck-versus-Prize decision more balanced. Exact information can therefore become more valuable for the specific Supporter choice.

This is a concrete decision-theoretic complement to the repository's broader Prize-belief work.

## Relation to the Iron Thorns Mail result

`results/iron_thorns_trainers_mail/` uses an observation-only target priority and does not let hidden Prize composition choose the Trainers' Mail target.

The present calculation explains why its G&H-first behavior is reasonable in the common one-missing-singleton subproblem. Mail misses move the Prize belief only modestly, while a Tag Call full search can create a genuinely different information state.

## Limits

This is a deliberately isolated belief calculation.

It assumes:

- no opponent mulligan bonus draws;
- no card is removed from the deck between successive misses;
- the singleton is known absent from all current hand and board cards;
- one missing singleton determines the Supporter choice;
- G&H and Gladion are both mechanically available;
- no other strategic costs or benefits distinguish the Supporters.

Real Trainers' Mail use can remove a selected Trainer from the deck, and its reveal can include other strategically informative cards. A full combined Iron Thorns policy needs a belief over all relevant hidden categories rather than one singleton.

## Next useful work

Use this posterior result as a policy constraint when combining:

- Trainers' Mail partial observations;
- Tag Call full-deck inspection;
- Guzma & Hala;
- Gladion;
- the Thunder Mountain and DCE package.

That combined model can then test how much additional value remains after the individually measured Mail and K1 effects interact.
