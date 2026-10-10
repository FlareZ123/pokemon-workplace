# Variable-depth ordered deck prefix with an exchangeable suffix

## Question

How much deck-order information must a Prize/top simulator preserve when effects reveal several consecutive upcoming cards?

The [single top-card pool](../prize_top_draw_pool/) models an exchangeable deck suffix, which is exact only when no relevant hidden deck order is known. The [top-two refinement](../prize_top_two_order/) keeps one additional position, but fails if the actor also knows a third card.

A variable-depth prefix provides a unified representation that preserves any finite number of ordered near-future positions while retaining a compact exchangeable remainder.

## Representation

`tools/prize_deck_prefix.py` uses:

- exact group counts across the current Prize positions, deck top, residual deck inventory, and drawn cards, supplied by the existing `PrizePoolBelief`;
- a tuple of `k` explicitly ordered deck cards immediately after the current top, all **still counted** as part of the residual deck inventory;
- a probability distribution over joint worlds that retains correlations among Prize positions, top, prefix, remaining group counts, and drawn cards.

The current top is deck position 0; the additional ordered prefix uses positions 1 through `k`.

It supports:

1. `from_exchangeable_pool(depth=k)`: sample an ordered prefix from the remaining card multiset without replacement.
2. `observe_deck_position(pos, group)`: condition on a source-authorized observation of any represented position.
3. `swap_top_with_face_down(position)`: perform an Arc Phone-like exchange of the current top and one eligible face-down Prize, leaving deeper deck positions unchanged.
4. `draw_top_and_advance()`: move the top into tracked drawn cards, shift the first prefix card to the new top, preserve subsequent known positions, and sample the next newly exposed deepest position from the residual **unreserved** deck cards.
5. `to_exchangeable_pool()`: forget order information while conserving all material card-group counts.

When no deeper card remains to refill the window, the prefix automatically shortens. For `k=0`, the model agrees with the existing exchangeable top-draw kernel. For `k=1`, it agrees with the earlier fixed top-two model.

## Independent six-card experiment

Take the distinct physical cards `A, B, C, D, F1, F2`, with two Prizes and four ordered deck positions. Assume:

- Prize0 contains B;
- Prize1 contains a filler;
- current top is A;
- the residual three-card deck inventory is C, D, and the remaining filler.

Arc Phone swaps A into Prize0 and puts B at the deck top. Subsequently the player draws B.

There are **720** initial five-position labeled deals (Prize0, Prize1, original top, original second, original third) without replacement. Exactly **12** satisfy the three initial constraints. Of those 12, four have C second. Of those four, two have D third.

The predictions change as additional ordered positions become known:

| Modeled deck knowledge before the swap | Prediction after drawing B |
| --- | --- |
| Inventory only, suffix order exchangeable | P(next top C) = **1/3** |
| Actor knows original second C | P(next top C) = **1**; P(following D) = **1/2** |
| Actor knows second C and third D | P(next top C) = **1**; P(following D) = **1** |

With second C and third D known, repeated draws advance the known sequence deterministically: outgoing B, then C, then D, then filler. The suffix-prefix depths after the first three draws are **2 → 1 → 0**, shrinking naturally as the deck approaches exhaustion.

Crucially, projecting a state where C and D occupy these known positions back to exact group counts erases their order. The conserved inventory remains the same while P(next C) falls from certainty to **1/3** under an unjustified exchangeable-order assumption.

## Test methodology

`results/prize_deck_prefix/reproduce.py`:

- exhaustively checks the source material probability against the 720 labeled ordered deals;
- compares all grouped k=0 and k=1 pool-world distributions to the **existing independent kernels**, before and after a physical swap/draw;
- asserts exact probabilities for the k=2 sequence;
- validates repeated draws, depth shrinkage, conservation and projected information loss;
- rejects impossible deep observations, overlong prefixes and extra draws after the modeled deck empties.

The substantive improvement is representational, rather than a new particular card-combination trick. It gives a simulator a way to retain only the near-future deck order whose knowledge can change a pending decision.

## Limits

- The deeper deck portion beyond the represented prefix is exchangeable. If the player knows card positions deeper than `k`, its exact information must first be lifted into a larger prefix. Failure to do so repeats the same abstraction error.
- The routine materializes the **first** `k` physical suffix positions in its hidden-world distribution even if the observer does not yet know their identities. Private knowledge is introduced by conditioning; different observers require separate posteriors and should be integrated with the existing epistemic event-trace layer.
- This is a finite grouped card-inventory kernel. It is not a complete game engine or a full physical card-instance ledger.
- A source effect that shuffles the deck must randomize the ordered prefix appropriately. This study only models top/Prize swaps and draws.
- Known second/third-card states are assumed to have arisen through a legal earlier look/placement; the model does not implement or adjudicate the corresponding Trainer or attack.
- The result concerns conditional state-transition probabilities, not tournament performance.

## Next research directions

Combine this ordered-prefix state with per-observer private peek histories. Then derive an exact criterion for **adaptive prefix depth**: represent precisely as far into the deck as observation history makes action-relevant, safely compressing unknown positions into exchangeable counts.
