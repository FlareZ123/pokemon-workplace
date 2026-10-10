# Selection-policy signaling from hidden Prize positions

## Question

If a player chooses a physical face-down Prize position when using Arc Phone, can the **chosen position itself** reveal hidden information to the opponent?

Yes, when the opponent has an informative model of the acting player's choice policy and the actor has learned information about the positions. This is a conditional inference about a declared strategy, not a universal claim about player behavior.

Arc Phone (`swsh11-152`) states: "Look at the top card of your deck. You may switch that card with 1 of your face-down Prize cards. (The cards stay face down.)" Earlier position work establishes that a player can know a face-down physical position after a deliberate placement, including Peonia-style exchanges. The act of selecting a position is observable even when the contents remain hidden.

## Exact two-world construction

Two face-down Prize positions contain one A and one B. The top card is a known X. The opponent has a prior assigning equal probability to two hidden states:

- `W1 = (Prize0=A, Prize1=B, Top=X)`;
- `W2 = (Prize0=B, Prize1=A, Top=X)`.

The actor privately knows the physical mapping through a previous legitimate observation or deliberate placement. The observer knows that the actor uses a stochastic policy:

- chooses Prize position **0** with probability **4/5** in W1;
- chooses Prize position **0** with probability **1/5** in W2.

When Arc Phone is played and the actor publicly chooses position 0, Bayes' rule gives

`P(W1 | chose position 0) = ((1/2)(4/5)) / ((1/2)(4/5)+(1/2)(1/5)) = 4/5`.

After the physical swap:

- the observed deck top becomes the outgoing Prize card;
- the opponent now assigns **4/5** probability to `Top=A`, up from **1/2** without considering selection policy;
- both Prize positions remain face down.

An actor who always targets the known A position would reveal it perfectly through their selected slot. An actor who chooses between slots with equal probabilities gives no slot-identity signal.

This demonstrates that source-legal choices can leak information about otherwise hidden cards. The effect is potentially important when the observer later exploits the top-deck identity, uses a face-down-position-targeting effect, or updates their beliefs about the opponent's hidden resources.

## Implementation

`tools/prize_position_top_swap.py` provides `condition_on_public_world_choice(likelihood_by_world)`. Each key is a complete grouped joint world, each value an assumed probability of the **specific observed action choice** in that world. The Bayesian conditioning step precedes `swap_face_down_with_top(selected_position)`, which applies the source-supported physical effect.

The regression checks the numeric witness independently using exact standard-library `Fraction` counts, tests deterministic and uninformative policies, checks a second-step physical swap, and rejects invalid likelihood domains and impossible choices.

The framework generalizes the earlier `condition_on_public_swap(likelihood_by_top)`: choosing whether to swap can signal top-card knowledge; choosing **which position** can additionally signal privately learned Prize-placement knowledge.

## Cautions and next work

- The selection policy must depend only on what the acting player could know. A world-conditioned likelihood table, used naively, could encode an impossible omniscient player. Callers must validate the acting player's information partition or explicitly model its private observations.
- These are conditional beliefs under a hypothesized actor policy. They are not measured competitive tendencies.
- The two-world example excludes effects such as Item lock, Card access contention, and turn sequencing.
- The result proves a posterior update for the specified information structure. It does not evaluate win-rate, practical value, or whether this would be a wise real-player signaling policy.

The next step is a **policy-admissibility validator** on the acting player's information partition, so a simulator cannot accidentally reward knowledge that player does not possess.
