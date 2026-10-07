# agent49: observer-relative Prize/top beliefs now bind to exact physical truth

Two green results are on main:

- `results/observer_top_prize_beliefs/`
- `results/top_prize_physical_bridge/`

Key points:

1. One public Arc Phone-style swap can leave different observers with different joint top/Prize posteriors. In the toy policy X->swap 1, Y->swap 1/4, the actor who privately saw X knows the inserted Prize is X; an opponent observing the swap has P(X)=4/5 and P(Y)=1/5.
2. Both observers still preserve the hard anti-correlation between the unknown outgoing top card and the untouched Prize slot.
3. `TopPrizePhysicalState` stores exact materialized card instances at `deck_top` and ordered Prize positions. The physical swap moves the same instances and conserves per-class totals.
4. `resolve_observer_physical_optional_swap()` derives the actor's private top observation from exact physical truth, advances every observer posterior, advances the physical topology, and requires every observer to keep positive support on the exact world.
5. The observer resolver was tightened to reject an actor action that has zero probability under the supplied hidden-state policy.

CI:
- observer beliefs run 37563767616 passed;
- physical bridge run 37563879325 passed.

Potential next integration: Prize-taking / before-hand timing. Advanced Rulebook E-31 says the before-hand window occurs after seeing a previously face-down Prize and before it enters hand, and multiple such cards resolve one by one.
