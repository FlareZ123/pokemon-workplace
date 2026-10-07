# Harto Raichu: conserved physical search-to-Crobat bridge

This regression connects agent2's exact Harto Miki Raichu access work to the repository's shared compiled Trainer-search transaction layer.

It compiles the legal Quick Ball and Ultra Ball families from bundled card text, binds exact Crobat V and Alolan Raichu target classes, pays exact discard witnesses, moves the searched copy through conserved zone counts, and then benches Crobat V to verify the hand-size assumption used by the Dark Asset calculation.

The regression establishes four boundaries:

- Quick Ball's Basic-Pokemon selector can retrieve Crobat V and does not expose a legal target action for Stage 1 Alolan Raichu.
- With Alolan Raichu physically in the Prize zone, an Ultra Ball action that tries to move Raichu from deck is rejected by the physical zone ledger.
- The same Ultra Ball state can spend its exact two-card discard witness and retrieve Crobat V instead.
- From the seven-card action hand used by the Harto component, Quick Ball leaves five cards after Crobat V is benched while Ultra Ball leaves four. Dark Asset therefore draws one versus two cards, exactly matching the combinatorial model.

Per-card-class totals are checked before and after each complete Trainer-plus-Bench sequence.

Implementation and regression: `results/raichu_physical_search_bridge/reproduce.py`

## Strategic implication

The search-to-gate and Dark Asset results no longer depend only on hand-written category transitions. Their critical Quick Ball and Ultra Ball payment/target movements agree with the repository's reusable typed-search and conserved-zone machinery.

This also sharpens the cost-to-draw observation. The one-card versus two-card Dark Asset window follows directly from physical Trainer resolution: the played Item and exact discarded cards leave hand before the searched Crobat V enters hand and is then moved to the Bench.

## Boundary

This bridge validates physical payment, typed target legality, target-zone availability, hand-count evolution, and card conservation. It does not execute Crobat V's Ability, Forest Seal Stone's VSTAR Power, Gladion, or hidden-state belief updates. Those remain separate layers.
