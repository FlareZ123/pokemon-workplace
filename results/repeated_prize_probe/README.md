# Repeated Prize probing and position memory

## Question

How much can a simulator lose by remembering exact Prize composition while forgetting which physical face-down positions have already been ruled out?

The loss can become very large across repeated position-sensitive actions.

Implementation: `tools/repeated_prize_probe.py`

Regression: `results/repeated_prize_probe/reproduce.py`

## State

The baseline has:

- six face-down Prize cards;
- exactly one singleton `TARGET`;
- five target-irrelevant cards;
- exact knowledge that the target is Prized;
- unknown initial target position.

A Peonia-like first action checks three distinct physical Prize positions.

If Peonia misses the target, those three positions are now known to contain replacement cards that are outside the target group.

Each later probe represents:

`Arc Phone -> Trekking Shoes`.

Arc Phone chooses one face-down Prize position and moves that card to the top of the deck. Trekking Shoes observes the new top card and may put it into hand.

If a probe misses the singleton target, the chosen physical Prize position is now another known non-target slot.

## Position-aware policy

After a three-card Peonia miss, the target is among exactly three untouched positions.

A position-aware policy tests a new untouched position on every later probe.

Conditional on the Peonia miss:

- one probe succeeds with probability `1/3`;
- two distinct probes succeed with probability `2/3`;
- three distinct probes succeed with probability `1`.

Including Peonia's initial 1/2 chance to take the target:

| Later probes | Position-aware total success |
| ---: | ---: |
| 0 | 50.000000% |
| 1 | 66.666667% |
| 2 | 83.333333% |
| 3 | 100.000000% |

The general singleton formula is:

`(n + min(m, P - n)) / P`

where:

- `P` is the Prize count;
- `n` physical positions were checked first;
- `m` later distinct probes are available.

## Composition-only forgetting comparator

Now collapse the state after every failed probe to only:

`exactly one TARGET remains among six Prize cards`.

That composition statement is true.

It omits which physical positions have been ruled out.

Under that lossy representation, every new Arc Phone decision sees the same exchangeable six-position state and assigns target probability `1/6` to the chosen slot.

After `m` probes, the comparator therefore behaves like repeated sampling with replacement:

`1 - (5/6)^m`

conditional on the Peonia miss.

The resulting totals are:

| Later probes | Position-aware | Composition-forgetting | Position-memory gain |
| ---: | ---: | ---: | ---: |
| 0 | 50.000000% | 50.000000% | 0.000000 pp |
| 1 | 66.666667% | 58.333333% | 8.333333 pp |
| 2 | 83.333333% | 65.277778% | 18.055556 pp |
| 3 | 100.000000% | 71.064815% | 28.935185 pp |

With three later probes, forgetting physical position memory understates the isolated line by:

`125/432 = 28.935185185 percentage points`.

## Why this is a representation error

No Prize shuffle is required between the failed probes.

A failed Arc Phone plus Trekking Shoes sequence tells the player that the chosen slot did not contain the target.

The replacement card moved into that slot by Arc Phone is also known to be outside the singleton target group because the target is still Prized.

The slot remains ruled out.

A position-aware belief therefore shrinks the candidate set after every miss.

A composition-only belief can still say the target is Prized with certainty while losing the information needed to shrink that candidate set.

This is a repeated-decision version of the earlier state-sufficiency counterexample.

## Card-channel feasibility

The concrete sequence can use:

- one Peonia Supporter;
- several Arc Phone Items;
- several Trekking Shoes Items.

The Advanced Player's Rulebook permits any number of Item cards during a turn while retaining the ordinary one-Supporter limit.

This result conditions on all required Trainer copies already being available and no applicable lock.

It measures the information and decision geometry after that availability condition is satisfied.

## Validation

The reusable model executes the position-aware policy directly on `PrizePositionBelief`.

The reproducer independently labels the singleton target's physical position from 0 through 5.

For the correct policy, exactly `n + m` labeled target positions succeed until every position is covered.

The composition-forgetting comparator is checked against the independent closed form:

`n/P + ((P-n)/P)(1 - ((P-1)/P)^m)`.

The regression checks zero through three later probes and reproduces the exact three-probe values:

- position-aware: `1`;
- composition-forgetting: `307/432`;
- gap: `125/432`.

## Strategic implication

The value of position information can compound across a sequence.

One forgotten bit of state does more than distort one action probability. It can cause a planner to repeatedly revisit an exchangeable abstraction after the real player has accumulated a growing set of impossible positions.

This is a general warning for hidden-zone simulators: sufficient state must preserve the history-dependent exclusions that affect future legal choices and probabilities.

## Limits

The model tracks one singleton target group.

Every failed probe is assumed to have a deterministic top-card observation such as Trekking Shoes, so the player learns whether the outgoing Prize was the target.

The calculation does not model the probability of assembling multiple Arc Phone and Trekking Shoes copies, Item lock, Item-search contention, deck-slot cost, hand disruption, or the value of the other moved cards.

It also assumes no effect randomizes the Prize positions between probes. An E-35-style shuffle would erase the accumulated physical-position exclusions.

## Next work

A useful generalization is a multi-target position policy where different Prize groups have different values and a probe can reveal information that changes which remaining position should be chosen next.

A broader simulator integration should preserve position exclusions inside the observer-specific hidden-state representation instead of reconstructing each decision from total Prize composition.
