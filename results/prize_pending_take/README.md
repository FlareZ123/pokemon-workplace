# Prize-taking pending queue and before-hand timing

## Question

Should a taken face-down Prize card move directly from the Prize zone to hand?

No. The supplied Advanced Player's Rulebook defines an explicit timing window after the card is seen and before it enters hand.

Implementation: `tools/prize_pending_take.py`  
Regression: `results/prize_pending_take/reproduce.py`

## Rule boundary

Advanced Player's Rulebook E-31 says that “before you put it into your hand” effects occur right after seeing a card that was previously face down and before putting it into hand.

It also states that when two or more cards with such effects are about to enter hand, their effects are applied one by one.

Chansey's Lucky Bonus is the concrete Prize example: a Chansey taken as a face-down Prize can go directly onto the Bench during this window.

Therefore an instantaneous:

`Prize -> hand`

transition loses a rules-visible intermediate state.

## Representation

`stage_prize_takes()` moves selected materialized Prize instances into a `prize_pending` zone and removes their physical Prize slots.

Each pending entry records whether that card was face down when taken.

This matters because some before-hand text explicitly checks that the card was taken as a face-down Prize.

`resolve_next_pending_prize()` resolves exactly the first pending card to a caller-specified destination. Ordinary resolution defaults to hand.

The destination can instead be an in-play object when a before-hand effect puts the card directly into play. In that line the instance never enters hand.

## Multiple Prize cards

The caller supplies the order of selected physical positions.

The pending queue preserves that order and permits only one-card-at-a-time resolution.

The regression stages two Prize cards in the order slot 1 then slot 0:

1. both leave the Prize topology and enter `prize_pending`;
2. the first resolves to hand;
3. only after that resolution does the second resolve;
4. the second is routed directly into play with a board-object binding.

The implementation does not claim which player or rule chooses an ordering when several orderings are legal. It preserves an explicit order supplied by the higher-level resolver.

## Observer coupling

`stage_prize_takes_with_observers()` composes the physical queue with the joint hidden-zone belief work.

For each selected Prize:

- the exact physical instance moves toward the pending queue;
- the taking player privately learns its grouped identity;
- other observers see the Prize slot disappear without automatically learning the identity;
- joint top/Prize correlations are preserved.

In the Arc Phone toy branch where top=A and the untouched Prize is B, privately seeing B as the taken Prize makes the actor certain top=A. The opponent remains at P(top=A)=1/2 because the identity was private.

## Finding

Prize taking has at least three separable boundaries:

1. remove a physical Prize position;
2. reveal the previously face-down card to the taking player and open the before-hand timing window;
3. route the card to hand or another destination after any applicable effect.

Collapsing those boundaries can skip legal before-hand effects, leak private identity information, or lose cross-zone Bayesian updates created by earlier Prize/top swaps.

## Conservation

All staged and resolved cards remain the same materialized `CardInstance` objects.

The regression checks per-class conservation across:

- Prize to pending;
- pending to hand;
- pending directly to in-play.

## Scope and limits

The module does not decide how many Prize cards an award grants or which Prize positions the player selects.

It does not interpret a specific before-hand Ability. The higher-level effect resolver chooses the destination and any additional effects.

The one-by-one queue is rule-backed. Ordering authority among several simultaneously eligible pending effects remains upstream because the cited E-31 text establishes sequential resolution without, in the excerpt used here, fully specifying a universal chooser rule.

## Next work

The next useful layer is to compile the existing `before_hand_prize_trigger` atom into this queue for a small audited card subset such as Chansey, Treasure Energy, Dream Ball, Greedy Dice, and Jirachi Prism Star.

That would connect card text directly to the new timing state without treating every pending card as a generic caller-directed route.
