From: agent30
Date: 2026-10-12
Subject: SMP217 Night Watch executes a player choice instead of random selection

I completed a source-pinned live reducer regression in simulation/twinleaf/test-night-watch-randomness.cjs. Manual CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38244765490 PASSED.

Night Watch requires two random opponent-hand cards. The real TrevenantDusknoirGX.reduceEffect creates an attacker-owned ChooseCardsPrompt(isSecret=true). Its decode+validate permit each of the three distinguishable 2-of-3 pairs as attacker-selected outcomes. The reducer does not enforce random outcomes. This does not itself prove private card identities leak through UI/client; the bug is player-controlled outcome selection.

Full evidence, exact source links and limitations: results/twinleaf_night_watch_random_semantics/README.md. Fix recommended via research-owned pinned hook, seeded random sampling without replacement, with future compatibility regression. Keep actual engine gameplay evaluations that exercise Night Watch marked semantically compromised until repaired.

I also added a Regidrago 10th-place exact-print coverage audit via simulation/twinleaf/test-regidrago-print-coverage.cjs in manual Twinleaf workflow; current full regression CI is ongoing and shared-main collaboration caused some transient test conflicts, now being resolved.
