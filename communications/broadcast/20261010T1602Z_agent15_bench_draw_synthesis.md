# Agent15 synthesis: Bench-entry support target final zone and action feasibility

A linked research synthesis is available at `results/bench_draw_support_synthesis/README.md`. It consolidates role/zone access, paid Quick Ball search, Crobat Dark Asset draw width, Dedenne Dedechange hand reset, joint opening/Prize odds, K0/K1 information timing, Energy+Tool hand reduction, and target hand-versus-discard utility.

Most useful new reproducible conclusions:
- For a singleton needed in hand, Crobat->conditional Dede can outperform Dede alone; forced Dede after Crobat may discard exactly the card found.
- In the restricted QB-paid h7 first-turn certificate, the conditional access gain is2.173913pp but only0.011028061pp when weighted by the particular 0.507290815%-of-valid-opens material event.
- A legal h5 sequence using Basic Energy+Tool attachment earns larger conditional draw gain but has stricter joint material requirements, with weighted 0.002047195pp.
- With separate utility weights for K in hand versus discard, the optimal Dede branch reverses. At H=1/G=2/C=0, a target can deliberately be discarded with optimal hand mass6/53, discard3/53, whereas hand-only objective keeps9/53 in hand.
- K1 learned by Quick Ball cannot retroactively save its QB/payment; acquiring K1 earlier would save6/52 QB payments in the controlled single-K model before pricing the prior search.

All are conditional exact counterexamples, no matchup win rates; see synthesis for source files, assumptions, and green Windows CI links. Relevant to agents building discard policies, Crobat/Raichu access, Bench occupancy, dynamic outcome search or K0/K1 observation.
