# Physical deck depletion gates same-line payload reacquisition

## Question

The provenance-aware temporal ledger in `reacquisition_discardability/` showed that an endpoint-required TM: Evolution can be discarded to Guzma & Hala when the Supporter later restores another copy.

Does the repository's canonical Trainer-search executor enforce the physical copy requirement behind that witness?

Yes.

This result composes Secret Box and Guzma & Hala as two exact typed search transactions over one conserved `ZoneCountState`.

Reproducer: `results/reacquisition_physical_bridge/reproduce.py`

## Concrete sequence

The controlled starting state contains:

- Secret Box plus three filler cards in hand;
- Tag Call, Guzma & Hala, two TM: Evolution, two Artazon, and one Jet Energy in deck.

Secret Box resolves first. Its exact three-card discard spends the filler, then its four typed outputs move one Tag Call, one TM: Evolution, one Guzma & Hala, and one Artazon from deck to hand.

Guzma & Hala then resolves from the resulting physical state. The optional two-card discard spends Tag Call plus the TM: Evolution retrieved by Secret Box. Its paid branch searches the remaining TM: Evolution and Jet Energy.

The final hand again contains:

- one TM: Evolution;
- one Artazon;
- one Jet Energy.

The first TM copy is in discard and the second TM copy is in hand. The played Secret Box and Guzma & Hala are also in discard. The Supporter budget is consumed, and every card-class total is conserved.

## Copy-depletion counterfactual

The reproducer repeats the same line with only one TM: Evolution in the starting deck.

Secret Box can still retrieve that TM. After Secret Box resolves, zero TM copies remain in deck.

The same abstract Guzma & Hala retrieval vector still asks for one Tool and one Special Energy. The physical transaction rejects the continuation when it attempts to move a TM from deck to hand because the canonical zone state has no copy left.

This is the missing execution gate behind the earlier DCI result:

**a currently held payload is transiently discardable only when the replacement route remains physically live after earlier searches and hidden-zone depletion.**

The counterfactual matters because a connector graph can continue to contain the edge `Guzma & Hala -> TM: Evolution` even after the last searchable TM has already left the deck. Exact zone execution removes that false positive.

## Two different constraints

The regression also checks a second failure mode. If Guzma & Hala has the replaceable TM but no other expendable card, its two-card optional discard cannot be paid. A replacement copy in deck solves payload retention but does not create a second discard card by itself.

The complete line therefore needs both:

1. enough physical hand material to pay the later discard; and
2. a searchable replacement copy for any required payload used as that material.

These are independent constraints.

## Relation to prior work

`reacquisition_discardability/` models exact hand provenance and endpoint retention, while its generated search outputs are caller-declared.

`trainer_search_transaction/` provides the complementary physical executor. It moves the played Trainer to a resolving zone, applies exact discard choices, moves exact typed targets from deck to hand, consumes Supporter quota, and checks card-class conservation.

This result composes those ideas on the same Secret Box into Guzma & Hala line. The provenance layer explains *why* a required card copy can be an acceptable discard. The canonical search layer proves *whether* the replacement actually exists in the deck at that moment.

## Modeling consequence

A future temporal policy bridge should carry two coupled views:

- a strategic provenance/retention view for deciding which copies are acceptable to spend;
- a canonical zone-count view for proving that searched replacements physically exist and for depleting them when retrieved.

Neither view is sufficient alone for state-dependent discard decisions involving reacquisition.

## Validation

The reproducer uses the repository's existing `execute_trainer_retrieval_transaction()` path for both actions. It asserts:

- Secret Box's first TM physically leaves deck;
- Guzma & Hala discards that exact card class from hand;
- the second TM physically leaves deck and restores the endpoint;
- the same second search is rejected after copy depletion;
- Supporter quota is consumed;
- per-card-class totals are conserved;
- a replacement route does not waive Guzma & Hala's two-card discard requirement.

## Limitations

This is a controlled microstate rather than an opening-hand probability model.

The compiled Secret Box and Guzma & Hala profiles are instantiated directly from their verified card text so the regression stays focused on transaction composition. The underlying repository compiler has separate tests for those profiles.

The test does not yet attach provenance labels to the canonical `ZoneCountState`. It demonstrates that the two layers agree on the concrete reacquisition witness and on the copy-depletion counterexample. A reusable bridge should synchronize the physical and provenance states after every action.

## Next useful work

Build a small synchronized state wrapper around `TrainerSearchExecutionState` and `ResourceLedgerState`. Every exact Trainer transaction should update both states and assert that their hand/discard projections agree. This would preserve generated-card provenance while inheriting canonical deck depletion, lock checks, and action quotas from the physical executor.
