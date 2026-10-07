# Prize-position deadlines can destroy information value

## Question

How should a position-aware Prize policy change when one required target must be acquired before there is time to gather more information?

A target deadline can force the first probe toward immediate coverage even when a different first position is strictly better under a relaxed horizon.

Implementation: `tools/prize_position_policy.py`

Regression: `results/prize_position_deadlines/reproduce.py`

## Deadline semantics

This result uses the same acquisition-deadline convention as the connector deadline models:

- deadline `0`: the target must be acquired by the current probe;
- deadline `1`: the current probe plus one later probe remain;
- deadline `2`: the current probe plus two later probes remain.

After each probe, every still-unacquired target's deadline decreases by one.

A negative deadline on an unacquired target is failure.

## Exact posterior

There are four face-down Prize positions with one A, one B, one C, and one filler.

The observer has equal posterior mass on four physical arrangements:

`(A, C, B, filler)`

`(C, B, filler, A)`

`(A, B, filler, C)`

`(filler, C, A, B)`

Each state has probability `1/4`.

The objective is to acquire A, B, and C before their respective deadlines.

A probe reveals and acquires the grouped identity at the selected physical position. The chosen position is then replaced by target-irrelevant filler.

## Relaxed horizon

Give every target deadline `2`, allowing three probes including the current action.

The exact success probabilities by first slot are:

| First slot | Success probability |
| ---: | ---: |
| 0 | 75% |
| 1 | 100% |
| 2 | 50% |
| 3 | 75% |

The optimal first probe is slot 1.

### Why slot 1 reaches 100%

Slot 1 is either C or B.

If it reveals C, the remaining posterior is split between:

`(A, C, B, filler)`

and

`(filler, C, A, B)`.

The next probe can inspect slot 2. B identifies the first state and A identifies the second. One final probe then takes the missing target from slot 0 or slot 3.

If slot 1 reveals B, the remaining posterior is split between:

`(C, B, filler, A)`

and

`(A, B, filler, C)`.

The next probe inspects slot 0. C versus A identifies the state, and the final probe takes the remaining target from slot 3.

The first slot therefore has pure information value that guarantees completion across all four hidden states.

## A is due now

Keep B and C at deadline `2`, and change only A to deadline `0`.

The exact first-slot values become:

| First slot | Success probability |
| ---: | ---: |
| 0 | 50% |
| 1 | 0% |
| 2 | 25% |
| 3 | 25% |

The optimal first probe shifts from slot 1 to slot 0.

Overall success falls from 100% to 50%.

### Why the information-rich slot becomes impossible

Slot 1 never contains A in any support state.

Since A has deadline `0`, probing slot 1 guarantees that A is still unacquired when its deadline expires.

Its excellent state-partitioning value cannot compensate for missing the current acquisition requirement.

### Why slot 0 reaches 50%

A is in slot 0 in exactly two of the four states.

Conditional on finding A there, the two surviving states are:

`(A, C, B, filler)`

and

`(A, B, filler, C)`.

The next probe at slot 1 reveals C or B and identifies which state remains. The final probe then acquires the third target.

Thus:

`P(success) = P(A is in slot 0) = 1/2`.

## Reusable policy kernel

`optimal_prize_acquisition_deadline_policy()` performs exact dynamic programming over:

- the physical Prize-position posterior;
- acquired target groups;
- the remaining deadline for each required target.

Every candidate position branches on its possible observation. The branch conditions the posterior, replaces the selected Prize slot with filler, updates the acquired set, decrements deadlines for still-missing targets, and optimizes the next probe.

The returned policy includes:

- exact optimal success probability;
- best first physical position;
- success value of every candidate first position.

## Independent validation

The regression uses a separate exact recursive enumerator over the four explicit hidden arrangements.

It conditions the labeled hidden states on each observation and optimizes later physical choices without calling the belief-policy solver.

The independent values match the reusable kernel exactly:

Relaxed deadlines:

`(3/4, 1, 1/2, 3/4)`.

A due now:

`(1/2, 0, 1/4, 1/4)`.

No Monte Carlo sampling is used.

## Strategic implication

Position information has a timing window.

A probe can be highly valuable because it resolves hidden state for later choices. That value collapses when an ALS prerequisite expires before the information can be converted into acquisition.

A planner therefore needs both:

- belief-state geometry over physical Prize positions;
- explicit deadlines for strategically required resources.

A raw number of probes remaining is insufficient when different targets expire at different times.

## Relation to connector deadlines

The result is the hidden-zone counterpart to the connector deadline work.

Connector models show that an urgent target can force a multi-output search to commit before future draws reveal which outputs are needed. Here, an urgent Prized target forces the physical probe to cover its possible positions before an information-rich probe can be exploited.

Both phenomena are instances of option value disappearing when a resource's acquisition window closes before the next information event.

## Limits

Deadlines refer to target acquisition.

A real ALS may require the acquired card to be played, attached, evolved, or otherwise executed before its strategic window closes. The current model also conditions on the probe action itself being available and usable.

Lock effects, Supporter contention, Item access, hand costs, replacement-card strategic value, and opponent disruption remain outside this isolated result.

## Next work

The strongest bridge is to move from acquisition deadlines to executable action deadlines. A Prized Supporter may need to reach hand before the Supporter channel is consumed, while an Item may remain playable later in the same turn unless Item lock arrives.

A concrete continuation can combine Peonia, Arc Phone, Trekking Shoes, and the canonical turn-action budget so the planner distinguishes acquisition from actual downstream execution.
