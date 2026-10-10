# Fair turn-order comparison for one Grand Tree Prize rescue

## Question

Arven can find Pokémon Communication before Gladion needs it,
but its first-turn Supporter access depends on turn order.
How large is that effect when **both players use the same deck**
and the event includes Communication already held, found by
natural draws, or fetched by Arven, without double-counting paths?

## Controlled game event

Consider a 60-card illustrative deck with:

* four Gothita Basic;
* one critical Gothorita and one critical Gothitelle;
* one Grand Tree ACE SPEC;
* one Pokémon Communication Item;
* G Gladion Supporters and A Arven Supporters;
* the remaining `52-G-A` cards as non-Basic filler.

The seven-card opening is accepted only if at least one Gothita
is in hand. The certificate further requires Grand Tree,
at least one Gladion, and at least one Gothita already in hand,
and neither evolution singleton in the opening hand.

The six Prizes must contain the singleton Gothorita while
excluding Gothitelle. Pokémon Communication may be either
in hand, or remain out of Prizes until it can be drawn or
searched by Arven. Gothitelle must remain deck-searchable
after two normal beginning-of-turn draws.

If Communication is in hand or naturally drawn by turn two,
Gladion on turn two can rescue Gothorita and Communication
can shuffle it back to deck, so Grand Tree can use the
Stage1→Stage2 effect.

Going second introduces an additional route: if Communication
is still in deck after the first natural draw and Arven is
either already in hand or drawn on that first turn, Arven
can search for it immediately. The next turn's Supporter
window remains available for Gladion.

Going first cannot use Arven on the first turn, so a
T2-prefetch route requiring Arven does not exist. Its
direct and natural-draw routes are retained.

No unsupported Stadium re-entry semantics are needed:
a single Grand Tree activation completes the target chain.

## Exact method

The model enumerates category counts in the initial seven-card
hand using multivariate hypergeometric weights, conditioned on
having a Basic. The rest of the deck is then sampled into six
Prize cards.

When Communication starts in hand, the Prize event is
`C(51,5)/C(53,6)` and the remaining Stage2 must avoid two
turn draws.

When it is not in hand, the Prize event is
`C(50,5)/C(53,6)`. Both Communication and the Stage2 must
avoid the Prize cards. The two sequential draws are modeled
with the possible Arven search **between** them, so the
second draw's physical deck population changes if Arven
removed Communication on turn one.

Where Arven is not already in hand, the number of Arven
copies among Prizes is hypergeometric. Conditioning on
that count is necessary to compute the probability of
drawing an Arven on the first turn and fetching
Communication. This avoids a false assumption that
every Arven not initially in hand is available in deck.

All probabilities are calculated as exact `Fraction`
values, with physical cards sampled without replacement.

## Controlled quantitative result

With two Gladion, one Pokémon Communication, and variable
Arven counts:

| Arven copies | Going first, turn-2 certificate | Going second, turn-2 certificate | Second-player gain |
|---:|---:|---:|---:|
| 0 | 0.016658% | 0.016658% | 0.000000 pp |
| 1 | 0.016658% | 0.027993% | +0.011336 pp |
| 2 | 0.016658% | 0.038448% | +0.021790 pp |
| 3 | 0.016658% | 0.048074% | +0.031416 pp |
| 4 | 0.016658% | 0.056922% | +0.040264 pp |

The nonzero first-player probability comes from already
holding or naturally drawing Communication. A first-turn
Arven increases only the going-second column in this
controlled event.

The probabilities are much smaller than the probability
of winning or setting up some functional deck; the
opening event requires a particular quartet of resources
and a critical singleton Gothorita actually to be Prized.
The gain is the *incremental access event probability*
at turn two for this exact card population, not a
general deck performance advantage of choosing to go second.

## Validation

`tools/grand_tree_arven_union_access.py` computes exact
category-weighted, Prize-conditioned, source-gated probabilities.

`python results/grand_tree_arven_union_access/reproduce.py`

The independent reproducer enumerates individual physical
card subsets for opening hands and Prizes and each possible
first/second natural draw in multiple small test universes.
On the first turn, its going-second policy fetches the
one physical Communication card from deck only if an Arven
is available. It then enumerates its second turn from
the reduced deck. Equality with the category exact
formula is asserted for both turn orders.

The first-turn Supporter rule is stated in the official
Japanese current basic rules:
https://www.pokemon-card.com/howtoplay/

Arven and Communication print texts are included in the
Expanded-legal bundled card pool. The bundled Advanced
Rulebook's Supporter quota and category-limited search
rules support the resource transitions.

## Scope

The model excludes other Pokémon search lines, extra
Item copies, draw engines, mulligan bonus draws, getting
the required starting resources through Abilities, opponent
disruption, live lock effects, early Knock Outs and
additional physical copies of either evolution card.

It also ignores possible strategic conflicts when Arven
can fetch a different Item needed more urgently.

It is a verified baseline for one narrow
turn-order-dependent connector competition, and it
illustrates the difference between a theoretical
Arven→Communication edge and its real timing-dependent
usefulness.

Related work:
[Arven-only prefetch certificate](../grand_tree_arven_prefetch/),
[direct Communication opening certificate](../grand_tree_opening_rescue_access/),
[physical Gladion-Communication bridge](../grand_tree_prize_rescue_bridge/).
