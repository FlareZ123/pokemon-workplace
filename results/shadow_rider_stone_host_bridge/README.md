# The V-host search chain rescues additional Prized Radiant Eternatus starts

## Finding

The champion Shadow Rider list can sometimes turn a Prized Radiant
Eternatus into a two-VMAX Climactic Gate launch even when there is
**no Shadow Rider Calyrex V initially in hand**. If Forest Seal Stone
is held, a paid Mysterious Treasure or Quick Ball can fetch a Shadow
Rider Calyrex V from the deck, that V can enter play and host Stone,
and Stone's Star Alchemy can find Hisuian Heavy Ball. Heavy Ball trades
itself for the Prized Radiant, which enters play from hand to use
Climactic Gate.

This is a legal additional path beyond the [previous naturally held V
Stone study](../shadow_rider_forest_stone_frontier/). It requires its
own conditional probability: **no V already held** and **at least one
V still in the deck**, with one search Item paid before looking at the
deck.

| Hypothetical Item discard policy | Prior Quick + Stone access | Added V-host bridge | Total exact access |
| --- | ---: | ---: | ---: |
| Unrestricted | 53.106724029% | **+0.293596073 pp** | **53.400320102%** |
| Psychic Energy only | 45.643268336% | +0.222205962 pp | 45.865474298% |
| Energy or extra held search Item | 47.890192495% | +0.242036509 pp | 48.132229004% |

Under unrestricted payment, the extra bridge consists of
**0.247432031 pp** using Mysterious Treasure and **0.046164042 pp**
using Quick Ball.

## Input deck and exact mechanics

The unchanged 60-card 2026 Aichi winner contains Shadow Rider
Calyrex V x3 (swsh6-74), Radiant Eternatus x1, Mysterious Treasure
x4, Quick Ball x1, Forest Seal Stone x1, Hisuian Heavy Ball x1, four
Shadow Rider VMAX and 11 Psychic Energy.

The setup uses one Basic-valid opening of seven, six Prizes and one
first-turn draw going second, with a non-Radiant Basic from the opening
chosen as Active and two VMAX remaining in deck for the final search.
In the new event, Radiant is Prized and Heavy Ball is in the
searchable deck, Stone is in hand, there is no Shadow Rider V in the
initial eight-card hand, at least one V is still in deck, and one
held Treasure/Quick Ball can be paid under the stated policy.
The other Basic opening is still a legal starting Active. The Item
search, V placement, Tool attachment, VSTAR Power, Heavy Ball, Radiant
Bench entry and Climactic Gate happen in that order.

The event is disjoint from earlier naturally available V-host routes
by construction. Alternative opponent restrictions, Board congestion,
future resource value and subsequent play are excluded.

## Exact probability identity

Implementation:
[tools/shadow_rider_stone_host_bridge.py](../../tools/shadow_rider_stone_host_bridge.py).
Reproducer: [reproduce.py](reproduce.py).

The earlier physical eight-category 60-card grouping is preserved.
Among the 13 otherwise grouped Basic Pokémon, exactly three are
Shadow Rider V. Among the 25 grouped filler cards, exactly one is
Forest Seal Stone. Let h be the number of these 13 Basics in the first
eight cards, p the number among Prizes, and f the number of the 25
fillers in the first eight. Under exact exchangeable physical labels:

P(Stone held, no V held, at least one V in deck)
= (f/25) × [C(13-h,3) - C(p,3)] / C(13,3).

Terms for impossible combinations are zero. Prize and draw
multiplicities are integrated using exact integer combinatorics and
reduced Fractions; the source Item's discard requirements and the
eligibility of the target V are checked before crediting any rescue.

Two independently labeled twelve-card toy cases model the exact physical
identity of a Stone, a V, Item payments, Prize positions, available
deck V targets, and VMAX stock. For all three payment policies their
full route probabilities match the grouped calculation exactly. The
reproducer also checks the published source prints and pins all three
actual-list exact rational totals.

## Limits and relevance

The increase is modest because many setup requirements must coincide,
but it establishes a concrete **search-for-the-enabler** path where a
tutor that cannot directly find the Prized Radiant can still enable
the rescue. This is a restricted source-access event, **not a match
win rate** or evidence that additional copies of these cards improve
a real deck. It assumes an uncontested Tool slot, an unused VSTAR Power,
a free Bench slot and permitted Item/Ability use. Strong competitive
claims require sequencing against realistic opponent actions, later
Energy management and alternative Star Alchemy targets.
