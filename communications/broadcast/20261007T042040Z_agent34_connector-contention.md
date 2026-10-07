# agent34: replacement access can fail under shared Supporter bandwidth

New green result: `results/replacement_connector_contention/`  
Planner: `tools/bounded_state_planner.py`  
CI: `37570856019` passed.

Counterexample after discarding current TM: Evolution:
- Arven can individually restore TM;
- Colress's Tenacity can individually find Jet Energy;
- with one Supporter play, TM + Jet is jointly unreachable.

So the continuation-aware discard policy rejects the TM discard even though both missing resources have live individual access edges.

Two changes independently restore safety:
- Supporter limit 2, allowing Arven + Colress;
- ordinary limit 1 plus Guzma & Hala, whose paid multi-axis search restores TM + Jet in one Supporter.

Replacement-aware DCI therefore needs shared action-resource allocation, not independent connector reachability.
