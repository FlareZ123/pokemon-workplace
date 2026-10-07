# Physical private-search target bridge

## Question

Can one exact privately selected arbitrary-card search target be moved into the actor's hand while the actor and opponent retain different, information-correct post-shuffle beliefs over the same physical truth?

Yes.

Implementation: `tools/private_search_target_physical.py`
Regression: `results/private_search_target_physical/reproduce.py`

## Composition

The bridge derives the actor's exact grouped Prize composition and the pre-search deck-plus-Prize pool from `SearchableDeckPhysicalState`. It then calls the private-target belief kernel with the actor's exact target group while other observers marginalize over the private target policy.

The exact target copy is materialized from deck into hand. One exact shuffled top is then materialized from the remaining deck. Per-class totals must remain conserved, and every observer posterior must assign positive probability to the exact top/Prize world.

## Six-card physical witness

The exact pool contains A, X, Y, and three fillers. Two Prize instances are A plus filler. The searchable deck therefore contains X, Y, and two fillers.

The private target policy is uniform over physical deck cards for every possible Prize composition. In the actual world, the actor selects X privately. The bridge then samples Y as the exact shuffled top.

Physical truth after resolution is private X in hand, exact top Y, and Prizes A plus filler. Card-class totals are unchanged.

## Observer divergence on shared truth

The actor has inspected the deck, knows A is Prized, and knows X was selected. The remaining unordered deck is Y plus two fillers:

- actor P(top=Y) = 1/3;
- actor P(top=A) = 0;
- actor P(top=X) = 0.

The opponent sees the private search and shuffle without target identity. Under uniform target selection:

- opponent P(top=A) = 1/6;
- opponent P(top=X) = 1/6;
- opponent P(top=Y) = 1/6;
- opponent P(top=filler) = 1/2.

Both beliefs assign positive probability to exact world top=Y, Prizes=(A, filler). Physical truth is shared while epistemic state remains observer-relative.

## Impossible target check

The regression attempts to privately search singleton A even though exact physical truth places A in Prize. The transition rejects the branch. Actor policy and physical materialization independently exclude it.

## Strategic interpretation

Private arbitrary-card search cannot reuse the public revealed-target bridge by simply hiding the target label afterward. The post-search deck distribution is already observer-dependent before the new top is drawn.

The physical selected card should be exact once the simulator commits to the branch. Belief state should expose that exact removal only to observers entitled to know it.

## Limits

This bridge starts from an already-open searchable deck state. It does not execute Computer Search's Trainer play or discard cost. It treats the target-selection policy as external and conditions on the search action occurring.

The selected private hand instance is materialized globally as physical truth. A future explicit hand-visibility layer may record which observers know that instance's identity.

## Next work

The strongest integration is an atomic Computer Search transaction combining play/discard payment, mandatory exact-one private selection, K1 update, observer-marginalized private target removal, exact shuffle top, and later continuation such as draw-to-N bandwidth.
