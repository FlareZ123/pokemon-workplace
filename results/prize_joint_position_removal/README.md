# Observer-relative Prize-position removal

## Question

When a player removes a chosen Prize card after a Prize/top-deck swap, can the observation affect beliefs about another hidden zone?

Yes. If the top card and Prize positions are correlated, seeing the removed Prize identity can also identify the hidden top card.

Implementation: `tools/prize_joint_position_removal.py`  
Regression: `results/prize_joint_position_removal/reproduce.py`

## Starting state

The regression begins from the observer-indexed Arc Phone-style state.

Before the swap:

- Prize slots contain exactly A and B in unknown order;
- the original top is X or Y with probability 1/2 each;
- the actor privately sees X;
- the public swap policy is X -> swap with probability 1 and Y -> swap with probability 1/4.

After the public swap with slot 0:

- the actor knows slot 0 contains X;
- the opponent assigns slot 0 probability 4/5 X and 1/5 Y;
- the new top is A or B with probability 1/2 each;
- the new top and untouched Prize slot 1 are perfectly anti-correlated.

## Prize removal event

Take the physical branch:

- top = A;
- slot 0 = X;
- slot 1 = B.

The actor removes slot 1 and privately sees B.

`remove_observed_prize_position()` conditions on that identity before deleting the position.

For the actor:

- P(top=A) becomes 1;
- P(top=B) becomes 0.

The actor learned the top card without looking at the top because the earlier swap made the zones correlated.

The opponent observes the public fact that Prize slot 1 left but does not see its identity.

`remove_unobserved_prize_position()` deletes the same position while marginalizing over its hidden identity.

For the opponent:

- P(top=A) remains 1/2;
- P(top=B) remains 1/2.

The earlier disagreement about slot 0 also remains: 4/5 X and 1/5 Y.

## Finding

Hidden-zone observations propagate through correlation, not only through the zone directly observed.

A Prize-taking transition therefore cannot always update a standalone Prize belief. If prior effects correlated Prize positions with the deck top, an observed Prize identity may carry information about the deck, while a private observation should leave an opponent's top posterior unchanged.

This is another reason to preserve joint hidden-zone distributions when card movement creates hard cross-zone constraints.

## Representation

The module provides three transitions:

- observed removal: condition on the chosen Prize identity, then delete the slot;
- unobserved removal: delete the chosen slot and marginalize its identity;
- observer-indexed removal: apply the observed or unobserved transition separately for each observer.

The public face-up mask shrinks with the physical Prize position.

## Scope and limits

The caller supplies the chosen physical Prize position. This module does not model the policy used to choose among several Prize positions.

The module updates information only. Exact physical movement is handled by the material-state layer.

The removed card has no destination here. Hand entry, before-hand trigger timing, Lost Zone or discard redirection, and Bench entry remain separate physical transition concerns.

## Next work

The immediate next step is a physical Prize-taking queue that stages selected Prize instances before hand entry. The Advanced Player's Rulebook E-31 defines a timing window after a previously face-down card is seen and before it enters hand, and says multiple such cards resolve one by one.

That physical queue can then use this observer-removal kernel so exact card conservation and asymmetric information advance together.
