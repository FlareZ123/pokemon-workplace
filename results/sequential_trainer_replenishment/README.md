# Sequential Trainer replenishment: Secret Box outputs fund Guzma & Hala

## Question

Can the repository's exact Trainer transaction layer execute a compound search line where cards created by the first connector pay the second connector's discard cost?

Yes.

This result executes a two-action physical card-class witness:

`Secret Box -> Guzma & Hala`

Implementation: existing `tools/trainer_search_transaction.py`  
Regression: `results/sequential_trainer_replenishment/reproduce.py`

## Exact starting state

The hand contains exactly:

- Secret Box;
- three pre-Box fodder cards.

The deck contains four Secret Box targets:

- one Item;
- one Tool;
- Guzma & Hala as the Supporter;
- one Stadium.

It also contains the Stadium, Tool, and Special Energy targets for the later paid Guzma & Hala branch.

There are no fourth or fifth pre-existing fodder cards in hand.

## Transaction 1: Secret Box

Secret Box first moves to the resolving-Trainer zone.

Its exact three-card discard witness consumes all three pre-Box fodder cards.

Its exact typed search witness then moves these four card classes from deck to hand:

- `sb_item`;
- `sb_tool`;
- `guzma_hala`;
- `sb_stadium`.

Secret Box then enters discard.

The Supporter budget remains unused.

## Transaction 2: Guzma & Hala

The retrieved Guzma & Hala is played from the new hand.

Its paid two-card discard branch uses:

- `sb_item`;
- `sb_stadium`.

Both cards entered the hand through Secret Box.

The generated `sb_tool` is protected with `max_copies=0` in the discard witness and remains in hand as a retained payload.

Guzma & Hala then retrieves its Stadium, Tool, and Special Energy targets and consumes the ordinary Supporter budget.

## Result

The compound line has:

- discard throughput: 5 cards;
- pre-Box discard fodder in the starting hand: 3 cards;
- downstream discard paid entirely from generated card classes: 2 cards;
- one generated Tool deliberately retained;
- exact per-card-class conservation across both transactions.

This is the execution-layer form of the abstract temporal resource counterexample.

## Why this matters

A static discard-capacity model can correctly answer whether one action's cost is payable.

Across a sequence, the relevant hand changes.

The first connector can create cards that are expendable after its own resolution. An exact state engine naturally captures this because the second discard witness is enumerated from the post-Secret-Box hand.

This provides a bridge between:

- `temporal_resource_replenishment/`, which models ordered resource production abstractly;
- `temporal_discard_replenishment/`, which finds the effect in the Aichi first-turn simulation;
- `trainer_search_transaction/`, which conserves exact card classes while executing each action.

## DCI / retention consequence

Raw hand growth still should not be equated with discardable production.

The regression protects one generated Tool while discarding two other generated outputs.

A future policy layer should decide which newly created card classes are acceptable payment under the current continuation, matchup, Prize state, and intended line.

The execution layer can then enumerate only discard witnesses allowed by that policy.

## Limits

This is a deterministic mechanical witness.

The card classes used for the side outputs are abstract representatives of the required Trainer categories. The result proves the sequencing and conservation property supported by the compiled Secret Box and Guzma & Hala profiles; it does not claim that every real deck state should sacrifice those categories.

It also does not evaluate the future strategic value of the discarded outputs.

## Next useful work

The next bridge is to project exact post-transaction hand state into a temporal resource profile without losing the ability to recover the underlying physical-card witness.

That would let a planner use compact replenishable-resource arithmetic and hand the chosen route back to the exact transaction layer for validation.
