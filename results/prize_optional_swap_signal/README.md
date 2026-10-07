# Optional Prize swap decisions can signal hidden information

## Question

If an opponent cannot see the top card viewed by Arc Phone, can they still learn about it from the player's optional decision to perform the swap?

Yes, when the swap policy depends on the hidden top card.

Implementation: `tools/prize_optional_swap_signal.py`  
Regression: `results/prize_optional_swap_signal/reproduce.py`

## Toy joint state

An observer begins with two equally likely hidden states:

- top deck = A, Prize = B;
- top deck = B, Prize = A.

The actor privately sees the top card.

## Deterministic policy

Suppose the actor swaps exactly when the top card is A.

If the opponent observes the swap occur, Bayes' rule collapses their pre-swap belief to:

- top = A;
- Prize = B.

After the public physical swap, the observer can infer:

- new top = B;
- Prize = A.

No card identity needed to be publicly revealed. The optional action itself carried the information.

If the actor declines the swap, the observer instead learns the original top was B.

## Graded policy

Suppose:

- top A -> swap with probability 1;
- top B -> swap with probability 1/2.

Before seeing the decision, A and B are equally likely.

Conditioned on observing a swap:

- `P(top=A | swap) = 2/3`;
- `P(top=B | swap) = 1/3`.

The public action therefore changes the opponent's posterior even when the policy is stochastic rather than deterministic.

If the actor swaps with probability 1 under both top-card identities, the action carries zero information and the posterior remains unchanged.

## Finding

Optional hidden-information actions are **policy-censored observations**.

The state transition alone is not enough to predict what an opponent learns. The observer must model the acting player's policy mapping hidden state to visible action.

This is structurally similar to the repository's setup-mulligan result: a public choice made after private information can reveal information about that private state.

## Why the joint Prize/top-deck state matters

The visible action can update both hidden zones because the pre-action top card and Prize composition may be correlated.

After conditioning on the action, the deterministic swap transition carries those correlations forward.

A model that updates only the top-card marginal or only the Prize marginal can miss the information transmitted through the choice.

## Limits

The regression uses a deliberately small two-state policy model.

Real Arc Phone decisions depend on broader game state, including the value of the known top card, Prize composition beliefs, deck access, hand resources, and future sequencing.

The observer is assumed to know the actor's policy probabilities. In practice an opponent has uncertainty over the policy itself, which would require another belief layer.

The model does not infer a competitive policy from game data. It only demonstrates the information channel created by optionality.

## Next work

A richer policy model could combine:

- the actor's private top/Prize joint belief;
- a utility model for swapping versus declining;
- an opponent prior over the actor's decision policy;
- Bayesian updating from the observed choice.

This would turn the static Arc Phone line into a small signaling game and connect Prize-state research to opponent-modeling work.
