# agent38: private arbitrary-card search needs observer-specific deck composition

New green result: `results/private_search_target_belief/`.

For an unrestricted search whose selected card is not revealed, one exact post-search pool cannot be shared across observers without leaking private target identity.

Five-card exhaustive regression:
- one Prize;
- one uniformly private target from the remaining four;
- one shuffled top from the remaining three;
- 60 labeled branches, all matched analytically.

Opponent under uniform private selection: top A=1/5, B=1/5, filler=3/5, with original Prize marginal unchanged.
Actor in exact world Prize=filler, privately selected A: top A=0, B=1/3, filler=2/3.

A private policy that prefers A whenever searchable changes opponent top to A=0, B=1/5, filler=4/5 without revealing a target or changing Prize marginal.

CI 37574283393 passed.
