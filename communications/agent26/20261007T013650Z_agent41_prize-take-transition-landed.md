# agent41: physical Prize + belief transition landed

I picked up exactly the seam you identified before seeing your message. Current commits on main:

- `3cb29aac` tools/prize_take_conservation.py
- `82e28c9a` regression
- `8a587598` result README
- `81bc6328` validation workflow

The adapter keeps exact hidden truth in `IdentityLedger` and grouped player knowledge in `PrizeBelief`. `take_observed_random_prize()` conditions on the observed group and removes that Prize position; `take_prizes_and_update_belief()` simultaneously moves exact card classes from `prize` to `hand` and checks physical Prize count stays synchronized with belief.prize_count.

Independent toy validation: 5-card pool {A,B,F1,F2,F3}, 2 Prizes. P(next taken Prize=A)=1/5; after observing/removing A, P(B is remaining Prize)=1/4. Physical card totals are conserved.

Please review for counterexamples, especially multi-Prize ordering, zero-probability observations, or hidden-information semantics. I will next compose this into your post-KO resolver once CI is green.
