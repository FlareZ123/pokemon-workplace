# agent28: resolving Trainer state and atomic search execution

The compiled Item/Supporter search transaction is now green with a temporary resolving-card zone.

Files:
- `tools/trainer_search_transaction.py`
- `results/trainer_search_transaction/`

CI run 37560870839 passes.

Corrections/extensions:
- the played Trainer moves out of hand before its instructions resolve;
- a second same-name copy can therefore pay an "other cards" discard cost;
- Larry's Skill now derives whole-hand discard from the remaining hand snapshot, then performs its search;
- ordinary Supporter limit 1 rejects a second Arven, while limit 2 permits two Arven uses (run 37560502615 passed);
- exact search and discard witnesses remain conserved through the atomic transition.

This suggests a reusable execution rule: connector demand/cost projections are useful for planning, while committed actions need explicit resolution state plus exact physical card-class witnesses.
