# Repeated-observation semantics change the optimal connector allocation

## Objective and setting

Previous work optimized a narrow Arc Phone -> Peonia target-recovery event using an abstract family of top-five arrangers. [The single-probe frontier](../arc_peonia_slot_frontier/) treated Rotom Phone and Pokédex as identical, since each can place a desired card from the visible top five on deck top. [The repeated-information result](../repeated_topfive_information/) identified an important difference: Rotom Phone shuffles its unchosen top-four into the deck, enabling new observations with later Items; Pokédex merely reorders the inspected five.

This experiment recalculates the **exact optimal slot allocation** with the complete immediate repeated-probe value and the actual name-specific four-copy limits.

A toy 60-card pool has twelve Basic starters, one singleton critical target, `K=A+P+R+D` fixed engine slots, and `F=47-K` expendable others. Copy constraints: `1<=A<=4` Arc, `1<=P<=4` Peonia, `0<=R<=4` Rotom, `0<=D<=4` Pokédex. Going second, the player accepts a seven-card opener with a Basic, sets six Prizes, draws the ordinary turn card, and can execute the sequential Item-to-Prize-to-Peonia line if the target is found in the deck before the Items are exhausted.

Every partition is evaluated with exact rational hypergeometric opening counts and the mathematically proved repeated-top-five observation probability. The optimizer exhausts every feasible slot split at each `K=2..16` and independently checks that every candidate is no larger than the recorded optimum.

## Revised optimal frontier

| K | Arc | Peonia | Rotom | Pokédex | Repeated-play optimum | Best one-probe approximation |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 3 | 3 | 0 | 0 | 0.180284% | 0.180284% |
| 7 | 3 | 3 | 1 | 0 | 0.252125% | 0.252125% |
| 8 | 3 | 3 | 2 | 0 | **0.323367%** | 0.320633% |
| 9 | 4 | 3 | 2 | 0 | **0.411756%** | 0.407570% |
| 10 | 4 | 4 | 2 | 0 | 0.524061% | 0.515200% |
| 12 | 4 | 4 | 4 | 0 | 0.753528% | 0.703037% |
| 13 | 4 | 4 | 4 | 1 | 0.866282% | 0.784330% |
| 16 | 4 | 4 | 4 | 4 | **1.146291%** | 0.983472% |

The complete test table covers every integer K from 2 to 16. Up through K=6, the two search/connectivity prerequisites Arc and Peonia dominate allocations to top-five arrangers. At K=7, a first Rotom copy becomes best. With K=8, the repeated-play model prefers **3 Arc + 3 Peonia + 2 Rotom**, whereas one-probe modeling prefers **4 Arc + 3 Peonia + 1 arranger**. Thus merging seemingly equivalent connectors changes the selected deck composition.

From K=9 onward Arc and Peonia reach their four-copy caps, Rotom continues to grow to four copies, then the first Pokédex enters the optimum at **K=13**. The first Pokédex is valuable after repeated Rotom shuffles create a new five-card inspection window. At K=16 the full 4/4/4/4 package reaches a 1.146291% raw access incidence, a substantial proportional difference from the one-probe approximation but still a very small absolute probability for a sixteen-card dedicated engine.

## Interpretation and reproducibility

Source: `tools/repeated_arranger_slot_frontier.py`; standalone `python -m tools.repeated_arranger_slot_frontier`. It uses the separately verified physical-information and opening kernels in `tools/repeated_topfive_information.py`, and compares the complete exhaustive maxima with `tools/arc_peonia_slot_frontier.py`.

This does **not** establish that running sixteen engine cards is sensible. They are competing for real deck slots and their alternative value is entirely excluded by the target-only event score. The analysis deliberately lacks opponents, Item and Supporter lock, extra draws/search, prize-card conditional utility, survival, bench constraints, evolving, Energy acceleration, and true win rates. It demonstrates a reproducible modeling failure mode: treating same-output **single-step** Items as interchangeable can reverse the winner of an exact fixed-budget card-allocation problem when their repeated sequencing semantics differ.
