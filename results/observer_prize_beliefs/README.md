# Observer-indexed Prize beliefs

## Question

Can one global Prize belief represent both players after a private Prize take?

No. The same physical Prize-zone event can reveal different information to different observers.

Implementation: `tools/observer_prize_beliefs.py`  
Regression: `results/observer_prize_beliefs/reproduce.py`

## Representation

`ObserverPrizeBeliefs` stores one `PrizeBelief` per observer for a single physical Prize zone.

All observer beliefs must agree on the number of Prize cards remaining. Their probability distributions over card-group composition may differ.

`update_for_prize_removal()` receives a visibility map:

- an observer present in the map learned the taken card's strategic group and uses observed removal;
- an observer absent from the map learned only that one Prize left and uses unobserved removal;
- a mapped value of `None` means the observer learned that the taken card belonged to the implicit filler category.

This separates the public material event from player-specific information.

## Private example

Both Alice and Bob begin with the same two-Prize hypergeometric belief over the five-card pool:

`A, B, F1, F2, F3`

Alice owns the Prize zone and privately observes that the taken Prize is A.

After removal:

- Alice assigns probability 0 that A remains Prized and probability 1/4 that B remains Prized;
- Bob, who saw only the Prize count decrease, assigns probability 1/5 to A remaining Prized and 1/5 to B remaining Prized.

Bob's posterior entropy is larger than Alice's.

## Public example

If both Alice and Bob are told that A was the removed Prize, both use the observed transition and their posteriors are identical:

- A remaining Prized: 0;
- B remaining Prized: 1/4.

This shows that observer divergence comes from information visibility rather than from the physical transition itself.

## Filler observation

If Alice privately learns that the removed card was filler, she conditions on that information.

Among the four possible identities left after an observed filler removal:

- A is the remaining Prize with probability 1/4;
- B is the remaining Prize with probability 1/4.

Bob still has the hidden-removal posterior of 1/5 for each singleton.

The regression checks this distinction explicitly.

## Finding

Hidden information belongs to observers, not to the physical game state alone.

A canonical simulator can keep one physical Prize-zone truth while carrying different beliefs for different players. This avoids granting the opponent private information and avoids withholding information that the taking player actually learned.

## Limits

This kernel tracks beliefs only. Physical Prize movement is handled by `prize_take_conservation.py`, while the temporary before-hand timing state is being developed separately.

All observers currently use the same grouped semantic vocabulary. A future model could allow observer-specific abstractions, though doing so would require explicit mappings between physical card classes and each observer's groups.

The exchangeable-position assumption remains. Position-aware Prize information needs a richer state.

## Next work

The immediate composition target is a player-relative hidden-state wrapper that combines:

- exact physical Prize-zone truth;
- observer-indexed Prize beliefs;
- event visibility;
- post-Knock-Out Prize awards;
- terminal game resolution.

A later policy model can use those beliefs for opponent inference and decision-making under asymmetric information.
