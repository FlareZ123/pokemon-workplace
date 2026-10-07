# Live-source Trainer transaction gating

## Question

Callers should be able to execute a Trainer action from current board and temporal lock sources without manually assembling the active restriction tuple.

Implementation: `tools/active_source_trainer_transaction.py`

Regression: `results/active_source_trainer_transaction/reproduce.py`

## Composition

The adapter queries `active_restrictions_for_player`, then delegates the resulting restrictions to the existing source-scoped Trainer transaction wrapper.

The established Trainer transaction remains the owner of search semantics, discard costs, zone movement, and Supporter budget consumption.

## Regression witness

Player A controls a live Vileplume Irritating Pollen source. Arven remains legal because the continuous restriction blocks Items rather than Supporters.

Player B then has a live Psyduck Headache temporal window affecting A. Arven is rejected for A while that window is active.

The same Headache window does not block B, its source player, so B can execute Arven under the same source collection.

After A's affected turn ends, the Headache window expires and Arven becomes legal for A again.

## Finding

The complete restriction lifecycle can feed a real transaction without storing derived lock booleans in canonical transaction state.

Board changes and turn-boundary changes can recompute the active set immediately before each action, while the underlying transaction engine remains unchanged.
