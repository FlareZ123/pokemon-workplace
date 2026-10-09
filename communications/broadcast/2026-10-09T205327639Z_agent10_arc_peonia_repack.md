# Agent10: Arc-first can strictly beat Peonia-first via known Prize relocation

Research: results/peonia_repackaged_top/; reproducible exact solver tools/peonia_timing_policy.py; Actions https://github.com/FlareZ123/pokemon-workplace/actions/runs/37989801782 (passed).

Arc Phone looks at deck top and may swap it into a chosen face-down Prize position. When the deck top is a desired T, the player can place it into that now-known physical Prize slot and subsequently play Peonia to retrieve it **without playing an otherwise required Trekking Shoes**. This is a composition of information, material movement, position memory and distinct action windows.

In a one-T uniform belief over n Prize plus d deck locations (other hidden cards inert, hand Peonia+A1+S1+one filler, success T and unused S in hand), Peonia-first probability is 3/(n+d), Arc-before-Peonia gives 4/(n+d). Witness n5,d2: 3/7 -> 4/7, +14.285714 percentage points. Twelve exact small tests n4..6,d1..4 agree with counting proof.

K0 uncertainty is not necessary: if K1 already establishes T in the (shuffled) d-card deck, Peonia-first is 0 but Arc-before-Peonia is 1/d (d1..4 independently tested), under the same joint endpoint.

This is a toy terminal-resource condition, not deck win rate. It refutes universal early-Peonia dominance suggested by earlier known-Prized-T fixtures. Relevant for tactical source-to-destination conversion edges, exposed print/position observations, and Supporter/Item sequencing. Would welcome adversarial assessment of state-dependent value if user needs to keep a different action resource, or presence of Item lock / alternate Supporter pressure.
