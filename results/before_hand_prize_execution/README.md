# Executing Prize-origin E-31 effects

## Question

Can the five typed Prize-origin before-hand profiles execute against the physical `prize_pending` queue without collapsing their different mechanics?

Yes for the direct movement and Item-resolution boundaries modeled here.

Implementation: `tools/before_hand_prize_executor.py`  
Regression: `results/before_hand_prize_execution/reproduce.py`

## Direct self-movement

Jirachi ◇ and Chansey move the pending physical Pokémon instance directly into play.

The executor checks the face-down Prize condition, the explicit "during your turn" condition, and the card-text Bench-space gate. Jirachi returns one additional Prize award. Chansey returns an additional award only when the supplied coin result is heads.

Treasure Energy moves its pending physical instance directly into the attachment relation and preserves the chosen holder ID.

Declining an optional direct trigger resolves the pending card to hand through the ordinary queue.

## Item play is a separate resolution state

Dream Ball and Greedy Dice do not use the direct self-movement path.

`begin_before_hand_item_play()` moves the pending Item instance into `resolving_trainer`. The pending entry is removed while the Item is resolving, so the state type distinguishes an unresolved Item from an ordinary queue that is ready for the next pending card.

`finish_before_hand_item_play()` moves the same materialized Item into discard after its effect finishes.

Dream Ball cannot finish until the caller confirms its Pokémon search/Bench effect was resolved.

Greedy Dice requires a coin result and returns an additional Prize award on heads.

## Hand-scoped Item locks

The regression activates every direct Item-play restriction from the source-zone audit while beginning Dream Ball.

All 42 restrictions are hand-scoped, so they do not match the `prize_pending` source and the special Item can begin resolving.

This demonstrates why the existing scalar `PlayerChannels.item_play` cannot safely stand in for every Item action. A false scalar channel can represent hand lock while erasing a legal special-source Item play.

## Additional Prize awards remain obligations

The executor returns `additional_prize_awards` rather than silently decrementing a Prize count.

A higher-level controller must choose the additional physical Prize position and stage that card through the same pending queue.

This preserves physical identity, observer-specific visibility, and E-31 timing for chained Prize effects.

## Limits

Dream Ball's searched Pokémon is not yet allocated by this module. Existing typed search execution can supply the exact target witness.

The executor accepts an explicit Bench object ID and attachment holder ID. It does not own the full board-capacity state.

Coin results are supplied as resolved stochastic outcomes. A policy or simulation layer remains responsible for sampling or enumerating branches.

The direct Item restriction input represents already-active prohibitions. Determining which lock effects are currently active belongs to the board/lock state layer.

## Next work

Compose Dream Ball with the typed search target allocator so the Item's searched Pokémon moves from the exact deck class into a concrete Bench object before the Item is discarded.

A second useful extension is recursive extra-Prize staging. Jirachi, Chansey, and Greedy Dice should be able to add another chosen physical Prize to the queue, including another E-31 card, without flattening the sequence into a count.
