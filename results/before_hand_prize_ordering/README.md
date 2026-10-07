# Owner-selected ordering for simultaneous E-31 Prize effects

## Question

When one Prize award produces several face-down cards with E-31 before-hand effects, is their processing order fixed by Prize position or selection order?

No. Official Pokémon Card Game Q&A gives a mixed-card example where a two-Prize award contains Chansey with Lucky Bonus and Dream Ball. The answer says the Chansey owner chooses which effect to process first.

Implementation: `tools/prize_pending_batch_order.py`  
Regression: `results/before_hand_prize_ordering/reproduce.py`

## Evidence

Advanced Player's Rulebook E-31 places the timing window after seeing a previously face-down card and before hand entry. It also states that when two or more cards with such effects are about to enter hand, their effects are applied one by one. Its two-Chansey example says the first Lucky Bonus effect is completed before the second begins.

The official Japanese Q&A adds ordering authority for mixed effects. After Knocking Out a Pokémon ex and taking two Prizes, if those Prizes are Chansey and Dream Ball, the owner of Chansey may choose whether Lucky Bonus or Dream Ball is processed first.

Source:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%89%E3%83%AA%E3%83%BC%E3%83%A0%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all

## Representation

`PendingPrizeBatchOrder` records the unresolved physical instance IDs that came from one simultaneous Prize award.

After the selected Prize cards have been staged and revealed to the taker, `choose_next()` can move any unresolved sibling from that batch to the queue head. This separates physical Prize selection from the later, information-aware effect-order decision.

A fixed queue order created before the taker sees the cards is therefore an unsafe policy representation when multiple E-31 effects are present.

## Nested additional Prizes are a barrier

Lucky Bonus, Wish Upon a Star, and Greedy Dice can create another Prize take while one sibling from the original award still waits.

The existing pending model places that additional Prize at the front of the queue. `PendingPrizeBatchOrder.choose_next()` refuses to move an older same-batch sibling across a pending card that is outside the original batch.

The regression demonstrates:

1. Chansey and Dream Ball are staged together.
2. Either one can be selected first after reveal.
3. If Chansey resolves first and takes another Prize, that new Prize becomes the queue head.
4. Dream Ball cannot be selected ahead of the nested Prize.
5. After the nested Prize finishes, Dream Ball becomes selectable again.

This preserves the E-31 rule that the chosen effect completes before processing another sibling effect.

## Finding

Simultaneous Prize selection and before-hand effect ordering are separate decisions with different information sets.

A policy engine should stage and reveal the awarded Prize cards first, then expose owner-controlled ordering among effects from that simultaneous batch. Any additional Prize work created inside the chosen effect must finish before control returns to the unresolved sibling batch.

## Limits

This result models the owner-controlled ordering witness established by the Chansey and Dream Ball Q&A. It does not claim a universal ordering rule for unrelated simultaneous effects outside this E-31 Prize context.

The wrapper assumes its batch is created immediately after one simultaneous Prize award is staged. Higher-level phase code remains responsible for opening that choice window at the correct time.
