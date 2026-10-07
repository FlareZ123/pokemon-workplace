# Prize-taking information asymmetry

## Question

When a player takes a face-down Prize card into hand and the opponent does not see its identity, should both players update to the same Prize belief?

No. The same physical transition can produce different information states for the two players.

Implementation: `tools/prize_take_information_asymmetry.py`  
Regression: `results/prize_take_information_asymmetry/reproduce.py`

## Two observation models

The taking player sees the card that leaves the Prize zone. Their belief therefore uses the observed-removal transition from `prize_take_conservation.py`:

`condition on observed group -> remove that group from the remaining Prize set`

An opponent who observes only that one Prize was taken cannot condition on its identity. Their update is:

`marginalize over every possible removed group -> remove one unknown Prize position`

`remove_unobserved_random_prize()` implements that second transition.

## Five-card labeled example

Start from a uniformly random two-Prize subset of:

`A, B, F1, F2, F3`

where A and B are modeled singleton groups and the three F cards are filler.

Suppose the taking player sees that the first Prize taken is A.

For the taker:

- A is certainly no longer Prized;
- B is the one remaining Prize with probability `1/4`.

For the opponent, who sees only that one of the two Prize cards left:

- A remains Prized with probability `1/5`;
- B remains Prized with probability `1/5`;
- a filler card remains Prized with probability `3/5`.

The regression independently enumerates every two-card Prize set and every equally likely removed position. The labeled enumeration matches the grouped belief transition exactly.

The opponent's posterior has higher entropy than the taker's posterior because the taker acquired private card identity information.

## Uniform-subset invariance

A stronger exact property holds under the exchangeable-position assumptions.

If the original Prize set is a uniform random `P`-card subset of a known pool, and an observer sees `r` random Prize positions removed without seeing their identities, then the observer's remaining Prize set is distributed exactly as a uniform random `P-r` subset of the same original pool.

The regression verifies this with:

- pool size 7;
- group A with 1 copy;
- group B with 2 copies;
- 3 original Prizes;
- 2 hidden Prize removals.

The resulting belief exactly equals a fresh one-Prize multivariate-hypergeometric belief from that seven-card pool.

This equivalence is useful because an opponent-side observer can sometimes update a random-Prize prior by reducing only the Prize count rather than reconstructing a larger hidden history.

## Strategic consequence

Private Prize information creates player-relative state.

After the same physical Prize take, one player may know a critical singleton is safely in hand while the opponent still assigns positive probability that it remains Prized. A game-state model with only one global `PrizeBelief` cannot represent both views.

Beliefs should therefore be attached to observers, while the physical ledger remains the single hidden source of truth.

## Limits

The transition assumes the removed Prize position is exchangeable with respect to identity.

If a previous effect revealed, rearranged, or otherwise distinguished specific Prize positions, the observer needs a richer position-aware belief.

The result models identity privacy only. Publicly revealed Prize-taking effects, hand-reveal effects, or card text that exposes the taken card should route the observer through an observed transition instead.

The model does not yet compose both players' beliefs with the post-Knock-Out terminal resolver or the temporary `prize_pending` timing state being investigated separately by agent26.

## Next work

A natural next layer is an observer-indexed hidden-state wrapper containing:

- one exact physical Prize-zone truth;
- the taking player's belief;
- the opponent's belief;
- observation events that update each belief according to what that player actually sees.

That representation can then support bluffing, opponent inference, and policy evaluation under asymmetric information.
