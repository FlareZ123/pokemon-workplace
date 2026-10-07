# Battle VIP Pass: multi-target direct-Bench hidden-state bridge

## Question

Can a two-target direct-Bench search preserve physical board placement and Bayesian target-set signaling in one atomic model?

Yes, for Battle VIP Pass's positive first-turn branch.

Implementation: `tools/direct_bench_hidden_state_bridge.py::execute_hidden_multi_direct_bench_trainer_transaction`  
Regression: `results/battle_vip_hidden_state_bridge/reproduce.py`

## Exact composition

The bridge combines:

- Battle VIP Pass's compiled two-Basic search profile;
- the shared Trainer lifecycle with its explicit non-hand staging destination;
- exact typed selection of two different Basic target classes;
- physical materialization of both copies as Bench objects;
- the compiled first-turn play condition;
- K1 Prize-composition inference from full-deck inspection;
- a public target-set policy label;
- removal of both selected groups from the deck/Prize pool;
- the following shuffle and exact sampled top;
- observer truth-support and card-total conservation checks.

## Witness

The hidden pool has singleton A, X, Y, and Z plus three fillers. Two cards are Prized.

The public policy chooses the set `XY` when A is Prized and both X and Y are unprized. The exact actor world has A plus one filler Prized.

Battle VIP Pass then places X and Y directly onto the Bench.

Observing `XY` conditions the other observer on A being Prized and X/Y being unprized. After X and Y leave the search pool:

- actor `P(top=Z)=1/3`;
- observer `P(top=Z)=1/4`.

The regression verifies these exact values.

## Physical result

After the transaction:

- Battle VIP Pass is in discard;
- X and Y have no hand counts;
- X and Y are stable `in_play` instances bound to two Bench objects;
- Z is the exact sampled `deck_top` instance;
- board and hidden physical state share the same identity ledger;
- all card-class totals are conserved.

## Strategic significance

Multi-target search signaling is a property of the entire public selection event, while physical state changes occur per selected copy.

For Battle VIP Pass, the observable pair of Pokémon may reveal information about the searcher's private Prize map. At the same time, both targets consume Bench capacity immediately and cannot be treated as transient hand resources.

This creates a useful general decomposition:

`private search information -> public selection event -> exact target removals -> destination-specific material state -> shuffled belief state`.

## Limits

The policy label `XY` is caller-defined. This result does not impose whether a real card's multi-target selection should be modeled as ordered or unordered. That depends on what the opponent can observe and on the strategic policy being studied.

The regression covers two distinct target classes. Repeated copies of one target class are supported by the underlying multi-removal primitive but are not exercised here.
