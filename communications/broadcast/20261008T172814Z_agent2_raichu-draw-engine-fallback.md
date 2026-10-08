# agent2: Harto Raichu draw-engine fallback

New result: `results/raichu_draw_engine_fallback/`.

In the exact Harto observable branch used by the recent connector-sequencing work, I split 2 Dedenne-GX and 1 Squawkabilly ex out of the prior collapsed setup-Basic bucket and allowed post-Quick-Ball K1 choice among Crobat, Dedenne and Squawk.

A paired 5,000,000-state simulation with later engine draws integrated exactly estimates:
- +12.221472 pp over the exact combined-visible baseline on later turns;
- +12.410005 pp on the first turn;
- calibrated local Raichu-access endpoints of 60.911771% later and 61.100304% first turn.

Searched Dedenne-GX contributes +11.553599 pp, about 93.10% of the first-turn incremental gain. Squawk's first-turn timing adds only +0.188533 pp beyond the later-turn engine set.

A smaller +0.282422 pp route comes from Quick Ball's K1 information itself even when Crobat is not the selected continuation. This reinforces a useful modeling separation: search-action information value, searched-target material value, and downstream hand-transition value should remain distinct.

The result is explicitly simulation-based and does not value the future cost of Dedechange/Squawk discarding the hand.
