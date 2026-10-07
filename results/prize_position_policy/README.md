# Prize position policy can favor information over immediate reward

## Question

If different Prized card groups have different strategic values, is the physical slot with the highest immediate expected reward always the best first probe?

No.

A two-step policy can rationally choose a lower-immediate-value position because its observation reveals more about where the remaining high-value cards must be.

Implementation: `tools/prize_position_policy.py`

Regression: `results/prize_position_policy/reproduce.py`

## Posterior state

Consider three face-down Prize positions with exact total composition:

- one A;
- one B;
- one filler.

The observer's position posterior is uniform over three states:

`(A, B, filler)`

`(A, filler, B)`

`(filler, A, B)`

Each state has probability `1/3`.

This posterior can also be viewed as the uniform six-permutation exact-composition prior conditioned on two binary exclusions:

- slot 0 is not B;
- slot 2 is not A.

Total Prize composition is exact in every support state. Composition entropy is zero.

Assign strategic reward:

- A = 2 utility units;
- B = 1 utility unit;
- filler = 0.

A probe reveals the selected outgoing Prize group, receives its utility, and replaces that physical slot with a target-irrelevant filler card. This is the information geometry of an Arc Phone-like chosen-slot swap followed by deterministic observation of the outgoing top card.

## One-probe values

The immediate expected values are:

| First slot | Immediate expected reward |
| ---: | ---: |
| 0 | `4/3` |
| 1 | `1` |
| 2 | `2/3` |

A one-step greedy policy therefore chooses **slot 0**.

## Two-probe values

Allow one later probe whose position may depend on the first observation.

The exact optimal two-probe values by first slot are:

| First slot | Optimal two-probe expected reward |
| ---: | ---: |
| 0 | `7/3` |
| 1 | `8/3` |
| 2 | `2` |

The best first action is now **slot 1**.

The first action with lower immediate expected reward becomes optimal over the longer horizon.

## Why slot 1 is informative

Slot 1 has three equally likely observations.

### Observe B

Only the first support state remains possible:

`(A, B, filler)`.

The next probe takes A from slot 0.

Total reward:

`1 + 2 = 3`.

### Observe filler

Only the second support state remains possible:

`(A, filler, B)`.

The next probe again takes A from slot 0.

Total reward:

`0 + 2 = 2`.

### Observe A

Only the third support state remains possible:

`(filler, A, B)`.

The next probe takes B from slot 2.

Total reward:

`2 + 1 = 3`.

Average:

`(3 + 2 + 3) / 3 = 8/3`.

The first slot-1 observation completely resolves which hidden state is present.

## Why immediate-greedy slot 0 is worse

Slot 0 gives A with probability `2/3` and filler with probability `1/3`.

If it gives A, two support states remain possible and B is split between slots 1 and 2. The best second probe gets expected B reward `1/2`.

That branch is worth:

`2 + 1/2 = 5/2`.

If slot 0 gives filler, the third support state is known and the next probe gets A from slot 1 for reward 2.

The full expectation is:

`(2/3)(5/2) + (1/3)(2) = 7/3`.

The lookahead-optimal first slot therefore gains:

`8/3 - 7/3 = 1/3`

utility units over the immediate-greedy first choice.

## Reusable policy kernel

`optimal_prize_probe_policy()` performs exact finite-horizon dynamic programming over `PrizePositionBelief`.

For every candidate physical position it:

1. computes each possible observed group;
2. conditions the position belief on that observation;
3. replaces the selected slot with target-irrelevant filler;
4. adds the observed group's strategic reward;
5. recursively optimizes the remaining probes.

It returns:

- optimal expected value;
- best first physical position;
- expected value of every candidate first position.

The reward scale is supplied by the caller. It can represent line completion value, recovery priority, tactical value, or another policy-specific utility model.

## Independent validation

The regression validates the dynamic program with a second exact method.

For each possible first slot, it exhaustively enumerates every deterministic second-slot choice for every possible first observation.

With three possible observations and three possible second positions, this checks all `3^3 = 27` continuation policies for each first action.

The independently enumerated two-step values match the dynamic program exactly:

`(7/3, 8/3, 2)`.

## Strategic implication

Physical Prize choice can contain **value of information**.

A position can be strategically best because the observation partitions future hidden states cleanly, even when another position has higher immediate expected card value.

This matters for any optimizer that selects hidden-zone actions using only one-step expected reward.

The correct objective can depend on:

- current position posterior;
- reward of each possible outgoing group;
- number of future position-sensitive actions;
- how each observation changes the posterior;
- replacement-card semantics;
- later action contention and deadlines.

The result therefore pushes Prize-state planning from static probability toward a finite-horizon belief-state control problem.

## Limits

The example uses one copy each of A and B plus filler.

Rewards are additive and fixed. Real card value is state-dependent and can change after one target is acquired.

Every probe is assumed to reveal the outgoing grouped identity and replace its Prize slot with filler.

The model does not include the probability of assembling the relevant Trainer sequence, lock effects, action quotas, or opponent disruption.

## Next work

A stronger policy model can let reward depend on the full game state and on which targets have already been acquired.

Another useful extension is a deadline-aware positional policy where the final probe must complete a specific ALS before a lock, attack, or turn boundary.
