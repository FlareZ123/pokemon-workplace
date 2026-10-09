# Finite deck order changes the value of Trekking Shoes after Arc Phone

## Question

How much does Trekking Shoes' optional discard-and-draw mode change the success of Arc Phone retrieval when the top of the deck and remaining Prize positions are correlated?

A controlled exact model finds a strict gain. The gain depends on **future deck order** and the remaining Item inventory. A "draws an unimportant filler after Shoes" approximation, used in the preceding [adaptive Arc Phone feedback model](../arc_phone_feedback_policy/), cannot capture this.

## Card text and interpretation

Arc Phone (`swsh11-152`) looks at the top card, then may exchange it with one face-down Prize card. Trekking Shoes (`swsh10-156`) lets the player take the top card into hand or instead discard that card and draw the next card. The choice is made *after* looking at the first card, before seeing the next. Both cards are Item cards. Source evidence: bundled Expanded card JSON and [Arc Phone](https://asia.pokemon-card.com/sg/card-search/detail/2749/) / [Trekking Shoes](https://asia.pokemon-card.com/sg/card-search/detail/3614/) card pages.

## Exact state

`tools/arc_phone_deck_order_policy.py` uses a normalized finite posterior over `(ordered Prize slots, ordered deck)`. The types are `T` (the singleton target), `A` (Arc Phone), `S` (Trekking Shoes) and `F` (inert filler). Initial Prize composition and deck composition are known, and each zone's permutations are independently uniform. Players only learn a deck-top card by playing an Item that looks at it, and only learn the outgoing Prize card after an exchange when another action reveals the top. The belief preserves the resulting cross-zone correlations.

An Arc action spends one available Arc Phone, observes top, then optimizes its optional exchange position or declining to exchange. A Shoes action spends one available Shoes, observes top, and selects whether to take it or discard it and draw the second card. Newly acquired `A`/`S` count as additional Item copies available in the same turn. After a Shoes draw the physical deck removes one or two cards; the posterior over the remaining deck order is retained exactly. The Bellman objective is the probability of acquiring `T` into hand with available Items.

## Result: discard-and-draw adds five and a half percentage points

Condition on three remaining Prizes with composition `(T,A,F)`, three deck cards with composition `(A,S,F)`, and an initial hand with **one Arc Phone and two Trekking Shoes**. Both zones have unknown physical order. The exact optimal policies give:

| Allowed Shoes actions | Target retrieval |
| --- | ---: |
| Look and take the first top card | `1/2 = 50.000000%` |
| Also allow discard shown top, draw second | `5/9 = 55.555556%` |

The extra `1/18`, or **5.555556 percentage points**, is a policy effect from access to the second deck position after a rejected first card. With `(T,S,F)` Prizes and the same deck/hand, the same exact gain occurs. These states represent partial games with three remaining Prize cards and an artificially small deck.

Additional exact state comparisons:

| Prize composition | Deck composition | Initially held Arc / Shoes | Take-only | Full Shoes |
| --- | --- | ---: | ---: | ---: |
| `(T,A,S)` | `(A,S,F)` | 1 / 2 | `5/9` | `5/9` |
| `(T,A,S,F)` | `(A,S,F)` | 2 / 2 | `5/8` | `2/3` |
| `(T,A,S,F)` | `(A,S,F)` | 3 / 2 | `8/9` | `11/12` |

The second four-Prize row gains `1/24`; the third gains `1/36`. These are specific conditional information states, and do not establish the typical value of Trekking Shoes or its deck inclusion.

## Independent verification

`results/arc_phone_deck_order_policy/reproduce.py` contains a separate labeled physical-world decision enumerator which does not use the production belief transitions. It enumerates explicit deck and Prize permutations, partitions the worlds on observations, implements Arc and Shoes actions over physical tuples, and exhaustively optimizes subsequent choices. Ten controlled cases, each with discard allowed and forbidden, match the production Bellman model exactly as rational fractions; expected gains are asserted independently.

## Scope and follow-up

The finite model fixes each zone's exact composition and makes top-of-deck order initially unknown. It omits Peonia, ordinary natural draw, search, Items elsewhere in hand, Supporter/Item lock, turn boundaries, opponent actions, and card value outside the terminal `T` acquisition objective. The sizes are chosen for independent exact enumeration and are far from realistic 60-card game states.

The next step is to connect this finite deck-order kernel to the initial six-Prize population model while modeling how K0/K1 search observations and other draw/search transitions constrain the joint posterior. Even a limited coupling should distinguish previously observed deck top from unobserved deck top and avoid granting free preview of discarded Shoes outcomes.
