# Canonical Trainer transactions can carry exact card-arrival provenance

## Question

The canonical Trainer transaction proves physical legality and card-class conservation, while `temporal_resource_ledger.py` explains which generated copy was later discarded.

Can those views be synchronized after every exact Trainer search transaction?

Yes.

Implementation: `tools/trainer_transaction_provenance.py`  
Regression: `results/trainer_transaction_provenance/reproduce.py`

## Bridge contract

`SynchronizedTrainerState` pairs:

- `TrainerSearchExecutionState`, the canonical physical zone, channel, and turn-budget state;
- `ResourceLedgerState`, the provenance-labeled zone state.

Construction succeeds only when forgetting provenance reproduces the exact canonical `ZoneCountState`.

`mirror_trainer_search_transaction()` accepts an already validated physical Trainer transaction together with the exact discard-selection and search-target witnesses used to execute it. It mirrors the same ordering into provenance state:

1. the played Trainer leaves hand for `resolving_trainer`;
2. exact discarded card classes leave the remaining hand;
3. exact searched card classes move from deck to hand;
4. those arrivals receive provenance `step:action`, such as `0:Secret Box`;
5. the played Trainer finishes in discard;
6. the provenance projection must equal the canonical physical post-state.

The physical executor remains authoritative for legality. The bridge adds history needed for state-dependent strategic evaluation.

## Concrete Secret Box into Guzma & Hala witness

The regression reuses the physical reacquisition line.

After Secret Box:

- the searched TM: Evolution in hand has origin `0:Secret Box`;
- the searched Guzma & Hala in hand has origin `0:Secret Box`.

After Guzma & Hala:

- the TM retrieved by Secret Box is in discard with origin `0:Secret Box`;
- the replacement TM in hand has origin `1:Guzma & Hala`;
- Tag Call is in discard with origin `0:Secret Box`;
- the played Guzma & Hala is in discard with origin `0:Secret Box`.

For both actions, forgetting origins exactly reproduces the canonical post-transaction zone counts.

This turns the prior verbal DCI statement into a mechanically linked witness: the card class remains required while one physical arrival instance is spent and another arrival instance restores the requirement.

## Physical aliasing can hide provenance choice

A second regression adds one TM: Evolution to the starting hand before Secret Box retrieves another TM.

Immediately before Guzma & Hala, two physically exchangeable TM copies are in hand:

- one with origin `initial`;
- one with origin `0:Secret Box`.

The exact physical discard selection says only “discard one TM: Evolution.” Both choices lead to the same canonical post-state because off-board copies of the same class are exchangeable there.

The provenance bridge therefore returns **two** valid witnesses:

- discard the initial TM;
- discard the Secret Box-retrieved TM.

Both project to the same physical zone counts.

This ambiguity is strategically meaningful. A physical class-count state can prove legality while leaving unresolved which historical copy a policy conceptually spent. If provenance affects discard valuation, the planner must preserve the branch or choose it explicitly rather than inferring one from the canonical counts.

## Relation to concurrent search materialization

`trainer_search_materialization/` carries exact compiled search-target witnesses into a physical identity ledger and rejects stale target witnesses after copies leave the deck. Its current boundary is scalar discard cost.

This bridge addresses the complementary side of the transaction: exact discarded classes and their arrival provenance. A future unified executor can combine compiled search materialization, exact discard witnesses, physical deck depletion, and provenance-sensitive policy evaluation without making the canonical state itself history-heavy.

## Modeling consequence

Two representations serve different jobs:

- canonical physical state should remain compact and exchangeable where physical copies are strategically indistinguishable;
- provenance state should be retained when a policy cares how a card entered the current zone or which earlier action generated it.

A projection relation can keep both synchronized without forcing every game-state consumer to pay the cost of historical identity.

This is especially useful for DCI and AMR. “This TM is discardable because Guzma & Hala will replace it” is a claim about one line's history and continuation, while “one TM is in hand and one remains in deck” is a physical-state claim.

## Validation

The regression asserts:

- synchronized construction exactly matches physical zones;
- Secret Box arrivals are labeled `0:Secret Box`;
- the TM later discarded to Guzma & Hala retains that origin;
- the replacement TM receives `1:Guzma & Hala`;
- every mirrored state projects exactly to the physical transaction result;
- a same-class hand with two origins yields exactly two provenance witnesses that share one physical post-state.

## Limits

The bridge currently mirrors Item/Supporter search transactions after the canonical executor has validated them. It does not itself compile card text or decide whether an action is strategically desirable.

Arrival provenance is relabeled when a card moves from deck to hand through the mirrored search. This is intentional history metadata, not a physical card identity. Physical class totals remain governed by the canonical transaction.

The wrapper currently enumerates provenance allocations when one class has several origins. Large hands with many same-class origins could require pruning or policy-guided selection.

## Next useful work

Use provenance witnesses as the input to a state-dependent discard policy. Compare policies that prefer post-search arrivals, protect initial singleton resources, or preserve cards with no live reacquisition route. Then execute the selected witness through the same canonical transaction path and measure how often provenance-aware choices change line feasibility in Aichi opening states.
