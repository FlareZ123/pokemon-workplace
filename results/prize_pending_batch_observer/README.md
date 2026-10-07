# Exact physical Prize batches and observer beliefs can resolve in lockstep

## Question

Can one transition keep physical pending-Prize order, exact card instances, observer-relative latent identities, destination visibility, and per-card resolution synchronized?

Yes for one simultaneous Prize batch without nested extra-Prize work.

Implementation: `tools/prize_pending_batch_observer.py`  
Regression: `results/prize_pending_batch_observer/reproduce.py`

## Composition

The adapter joins four existing layers:

- `PrizePendingTakeState` for conserved physical Prize instances;
- `PendingPrizeBatchOrder` for exact sibling selection order;
- `ObserverPendingPrizeBatchBeliefs` for latent per-card grouped identities;
- destination visibility for hand, discard, and Lost Zone.

`stage_prize_batch_with_latent_observers()` stages one simultaneous physical award and conditions the actor on the true selected Prize groups while retaining those identities latently for other observers.

`resolve_batch_instance_destination()` selects a physical sibling by instance ID, moves that exact card to its destination, conditions observers according to destination visibility, removes the matching latent variable, and advances the unresolved sibling batch.

When the final sibling resolves, the observer state projects back to the ordinary top/Prize joint-belief representation.

## Regression

The witness again uses the Arc Phone correlation state with exact physical truth:

- top = A;
- selected Prizes = X and B.

Both physical Prize cards are staged together. The actor sees X and B while the opponent starts at P(top=A)=1/2.

Resolving B to discard first:

- moves exact instance `prize-b` to discard;
- makes B public;
- changes opponent P(top=A) to 1;
- leaves exact `prize-x` as the unresolved sibling.

Resolving X to Lost Zone then moves the exact second instance, empties the Prize and pending topology, and preserves the posterior.

A counterfactual branch sends B to hidden hand and X to public Lost Zone. The opponent finishes at P(top=A)=1/2 because the decisive B evidence remained private.

All branches preserve card-class totals.

## Scope

This adapter covers one simultaneous batch and destination-level resolution. It does not yet compose nested additional Prize cards created by Lucky Bonus, Wish Upon a Star, or Greedy Dice.

The sibling-order wrapper already treats such nested work as a barrier. A future extension can add observer-relative latent identity for nested cards while preserving that barrier.

## Architectural implication

Physical instance order and observer belief order should share the same stable card key.

Using exact pending instance IDs for both layers makes it possible to reorder a known sibling, apply its destination visibility, and update the corresponding latent identity without relying on positional coincidence after earlier siblings have moved.
