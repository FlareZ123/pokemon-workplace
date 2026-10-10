# Drawing after Arc Phone: conserved residual deck correlation

## Question

When Arc Phone exchanges a face-down Prize card with the known top card of the deck, the outgoing Prize becomes the new deck top. If the player later draws that outgoing card, what can they infer about the **next** deck top and the untouched Prize cards?

A naive model may assign probabilities independently to the next draw and remaining Prize identities. That can invent impossible worlds where a unique card appears in two zones at once.

## Model

`tools/prize_top_draw_pool.py` represents a closed, initially shuffled pool divided into:

- ordered individual Prize positions;
- one current top-of-deck card;
- a remaining exchangeable deck suffix represented by exact group counts;
- cards already drawn from the modeled pool, represented by exact group counts.

Every world conserves the same original multiset of card groups, including unmodeled filler cards. The transitions are:

1. `observe_top(group)`: condition without moving the top card;
2. `swap_top_with_face_down(position)`: exchange the top and one face-down Prize, conserving all card counts;
3. `draw_top_and_refill()`: move the top into tracked drawn cards and expose a new top from the remaining deck, weighted by the exact residual group multiplicities.

The refill assumes that the **unobserved suffix of the deck is uniformly exchangeable** conditional on the modeled state. That assumption holds for the independently shuffled oracle below and must be reconsidered after effects that reveal, order, place, or manipulate deeper deck cards.

A projection back into the existing joint Prize/top belief preserves position and top marginals, while intentionally discarding the residual pool/hand inventory.

## Exact labeled-card experiment

Use five distinct physical cards:

`A, B, C, F1, F2`.

The two Prize positions and first two ordered deck-top positions are initially a uniformly shuffled assignment without replacement. There are **120** possible ordered four-position deals.

Suppose the player knows original top A, swaps A with face-down Prize0 using Arc Phone, then draws the new top and observes it was B.

Exactly **six** labeled initial deals satisfy original top A and outgoing Prize0 B. Condition on that event. After the draw, the physical zone pattern is:

- Prize0 is certainly A;
- the drawn card is certainly B;
- Prize1 is C or filler;
- the new top is C or filler.

An exhaustive oracle over the six labeled deals proves:

| Event after observing and drawing B | Probability |
| --- | ---: |
| C is at untouched Prize1 | **1/3** |
| C is now the next deck top | **1/3** |
| C is simultaneously in Prize1 and at deck top | **0** |

Multiplying the two correct marginals independently would invent an impossible probability **1/9** for C occupying both positions.

If an observer sees the public Arc Phone exchange and subsequent draw without learning that the outgoing card was B, while still knowing initial top A for this comparison, the probability that the next top is C is **1/4**. The extra private observation therefore changes the correct next-card forecast from 1/4 to 1/3.

These quantities are **conditional physical combinatorial probabilities**, not empirical gameplay frequencies.

## Independent verification

`results/prize_top_draw_pool/reproduce.py` enumerates all `5P4=120` labeled physical assignments independently of the compressed dynamic program, filters the six eligible histories, and constructs the post-draw Prize, top, remainder, and drawn-card inventories.

The regression compares **every** resulting grouped joint world to its exact-`Fraction` physical oracle, checks conservation in the underlying kernel, verifies the anti-correlation and both observer information conditions, and rejects impossible pool counts or attempts to refill when the deck has no remaining card.

## Scope and limits

The source-backed game mechanics are the ordinary top-card draw and Arc Phone's face-down Prize swap. The specific five-card example isolates a tiny legal-like material configuration; it does not implement item play timing, legal starting setup, Supporter contention or any other deck component.

The pool's remaining deck cards are exchangeable in order. If an effect gives the player information about the **second** or later deck card, the next-card draw requires a richer deck-position belief. Reconstructing a naive hypergeometric pool after such effects would destroy information and could make this model wrong.

The model has only one current top card, assumes a next card exists for each call to `draw_top_and_refill`, and does not model the complete game hand, a material `IdentityLedger`, or Prize taking itself. It tracks only draws from the closed research pool. An observer who sees the drawn card may condition on it, while one who does not should marginalize, rather than assuming they both received the same information.

## Next

Integrate the residual-deck inventory with the physical-instance and observer-event bridge. A later experiment should introduce a known second deck card and demonstrate where the exchangeable-suffix refill approximation breaks.
