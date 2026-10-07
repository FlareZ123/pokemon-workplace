# State-dependent Prize utility changes the optimal positional policy

## Question

Can a finite-horizon Prize-position planner always reduce strategic value to a fixed reward for each outgoing card group?

Combo completion creates acquired-set-dependent value. A finite deadline can make the best physical position differ from the choice produced by fixed per-card rewards.

Implementation: tools/prize_position_policy.py

Regression: results/prize_terminal_utility_policy/reproduce.py

## Exact posterior

Consider four face-down Prize positions. The exact composition is one A, one B, one C, and one filler. The observer has equal posterior mass on three physical arrangements:

(C, A, B, filler)

(filler, A, C, B)

(C, filler, B, A)

Each state has probability 1/3. Composition entropy is zero, so the uncertainty is entirely positional.

## Deadline utility

Two probes remain before a decision deadline.

Terminal utility gives +10 when both A and B have been acquired and +6 when C has been acquired. Acquiring all three is worth 16.

A and B represent a conjunctive line, such as two ALS resources that matter together by the deadline. C represents an independent fallback resource.

This objective has no exact fixed additive decomposition over individual groups. Singleton A and singleton B each have zero terminal utility, while the pair {A, B} has utility 10.

## Fixed additive proxy

A natural proxy splits the combo reward across its components: A = 5, B = 5, C = 6.

The existing additive finite-horizon planner gives these two-probe values by first slot:

| First slot | Additive proxy value |
| ---: | ---: |
| 0 | 28/3 |
| 1 | 9 |
| 2 | 11 |
| 3 | 28/3 |

The proxy chooses slot 2.

## State-dependent terminal policy

The new optimal_prize_terminal_policy() carries the acquired target set through the belief-state dynamic program and evaluates utility at the finite horizon. The probe budget is an upper bound, which permits early stopping when another probe cannot improve terminal value.

The actual terminal-utility values by first slot are:

| First slot | Terminal utility |
| ---: | ---: |
| 0 | 6 |
| 1 | 22/3 |
| 2 | 6 |
| 3 | 26/3 |

The terminal-optimal first action is slot 3.

### Why slot 3 wins

Observing slot 3 identifies which hidden state is present.

If slot 3 is A, the state is (C, filler, B, A). The second probe takes B from slot 2 and completes the pair for utility 10.

If slot 3 is B, the state is (filler, A, C, B). The second probe takes A from slot 1 and completes the pair for utility 10.

If slot 3 is filler, the state is (C, A, B, filler). The second probe takes C from slot 0 for utility 6.

The expectation is (10 + 10 + 6) / 3 = 26/3.

### Why slot 2 loses under the acquired-set objective

Slot 2 contains B in two support states and C in the third.

After observing B there, A is split between slots 1 and 3. One probe remains. Trying one A position succeeds half the time, producing expected combo utility 5. C is known at slot 0 in both remaining states, so taking C guarantees utility 6.

After observing C in slot 2, one probe remains while both A and B are still required for the pair. Terminal utility is therefore 6.

Slot 2 is worth exactly 6 under the acquired-set objective.

The first action selected by the additive proxy loses 26/3 - 6 = 8/3 terminal utility units, even if later play uses the correct state-dependent continuation.

## History dependence

The same physical posterior yields a different one-probe decision when A has already been acquired before the modeled window.

With initial_acquired=("A",), slot 2 becomes optimal and expected terminal value is 26/3. B can immediately complete the pair while C retains its fallback value.

The relevant policy state therefore includes the acquired strategic resource set in addition to the Prize posterior and remaining horizon.

## Validation

The regression checks the dynamic program against an independent exact enumeration.

For each first slot, it enumerates every deterministic mapping from first observation to second physical slot. Four possible observations and four possible second positions produce 4^4 = 256 continuation policies per first action.

The independently enumerated terminal values match (6, 22/3, 6, 26/3).

The regression also checks the additive proxy values, composition certainty, the initial_acquired continuation, and early stopping after utility is saturated.

## Strategic implication

Finite-horizon hidden-zone planning needs utility state capable of representing prerequisites, substitutes, fallbacks, and deadlines.

A fixed scalar value attached to each card group can still serve as a local heuristic. It cannot encode every ALS completion objective.

A stronger planner can use acquired-set utility and later connect it to board state, Supporter contention, action quotas, locks, and turn boundaries.

## Limits

This is a positional belief-state counterexample rather than a full-match model.

Probe availability is conditioned on the relevant actions already being accessible. The model omits the cards used to create probes, Item lock, Supporter contention, opponent disruption, and downstream match value after line completion.

The caller supplies terminal utility. Estimating realistic utility from match outcomes remains a separate research problem.

## Next work

The next useful bridge is explicit action deadlines from the turn-state infrastructure. A positional plan should be able to ask whether its remaining information-gathering sequence fits before an attack ends the turn, a lock removes access, or a one-per-turn channel is consumed.

A second direction is deriving terminal utility from a concrete ALS rather than assigning abstract values by hand.
