# Nested additional Prizes preserve both queue barriers and hidden information

## Question

When a Prize-origin effect creates an additional Prize while siblings from the original award remain unresolved, can the simulator preserve the physical barrier and observer-relative identity uncertainty at the same time?

Yes.

Implementation extensions:
- `tools/pending_prize_batch_identity_belief.py`
- `tools/prize_pending_batch_observer.py`

Regression: `results/nested_prize_observer_barrier/reproduce.py`

## Background

The existing `PendingPrizeBatchOrder` already establishes a sequencing rule for Lucky Bonus, Wish Upon a Star, and similar effects: an additional Prize is prepended to the pending queue and an older sibling cannot be moved ahead of that nested work.

The observer layer previously lacked the same geometry.

## Transition

`prepend_additional_pending_for_observers()` removes one remaining Prize position, prepends its grouped identity to the latent pending tuple, and conditions only observers who can see that Prize identity.

`prepend_additional_prize_with_latent_observers()` performs the matching exact physical transition with `stage_additional_prize_front()`, then rebinds the original sibling-order controller to the enlarged queue.

The integrated state now validates two separate invariants:

- the full physical pending queue exactly matches the belief pending-instance queue;
- every unresolved original sibling remains present inside that queue.

`resolve_nested_queue_head_destination()` resolves a nested head without consuming the unresolved-sibling set. Once nested work clears, sibling choice becomes available again.

## Regression witness

The physical truth is:

- top A;
- original simultaneous pending siblings X and B;
- remaining Prize C.

The opponent initially has two hidden worlds and P(top=A)=1/2.

The actor takes X and B together, then a nested effect takes C. The queue becomes:

`C -> X -> B`

The nested C identity is private to the actor. The opponent retains P(C at nested head)=1/2 and P(top=A)=1/2.

Attempting to choose B while C is still at the head is rejected by the original batch-order barrier.

When C resolves to public Lost Zone, the exact physical C moves there and the opponent conditions on that public identity, raising P(top=A) to 1. The queue returns to `X -> B`, after which the original siblings can again be selected and resolved.

Card-class totals remain conserved through the complete physical sequence.

## Architectural implication

Nested effect sequencing and hidden-information sequencing are the same queue at different abstraction levels.

A simulator that models only physical barriers can still leak or erase information. A simulator that models only latent identities can accidentally let an older sibling jump across unfinished nested work. The stable pending-instance ID supplies the join key that keeps both layers synchronized.
