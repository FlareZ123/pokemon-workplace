# Exact mixed-zone prior threshold for Arc Phone versus Trekking Shoes

## Result

A precise switch exists between Item mixes when the player assigns a partial prior probability to a singleton target being Prized. This extends [the K0 location frontier](../arc_peonia_k0_item_frontier/) and [K1 Shoes substitution](../arc_peonia_shoes_tradeoff/) by optimizing actions **before** knowing whether T is in the Prizes or the deck.

Controlled experiment:

- One target T is Prized with probability p and, conditional on that, uniformly among six facedown Prize slots.
- With probability 1-p it is uniformly among 46 hidden deck positions.
- Every other hidden card is inert filler F.
- A Peonia, spare F replacement-payment card, and exactly four usable Items are held: a Arc Phone and 4-a Trekking Shoes, with a=0..4.
- Items may be sequenced freely, observations are revealed only when their corresponding card is used, and Peonia may be played once at any point.

The **optimal initial Item mix** for maximizing the probability of getting T into hand is:

| Prior p that T is Prized | Optimal Arc Phone / Shoes mix |
|---|---|
| 0 <= p < 6/29 | 0 Arc / 4 Shoes |
| p = 6/29 | Any of 0/4, 1/3, 2/2, or 3/1 |
| 6/29 < p < 1 | 3 Arc / 1 Shoes |
| p = 1 | 3 Arc / 1 Shoes or 4 Arc / 0 Shoes |

The threshold \`6/29 = 20.68965517%\` is **exact**, and at this prior the four tied mixes have probability of retrieval \`7/29 = 24.13793103%\`.

The globally optimal value is

\`V*(p) = max[ p/2 + 8(1-p)/46, p + 2(1-p)/46 ]\`.

At a uniform prior across six Prize and 46 deck positions, \`p=6/52=3/26\`, so four Shoes is optimal. Once a deck search or other evidence raises the posterior probability of T being Prized past 6/29, three Arc and one Shoes become optimal *under this specific model*.

## Derivation from physical location budgets

Each action can expose a limited number of initial target positions before resources run out: Peonia up to three Prizes, Arc Phone one deck-top observation per copy and at most one Prize exchange per copy, and Shoes at most two deck-top positions per copy through its conditional discard-and-draw choice.

For each fixed four-Item mix, the following nondominated (Prized slots covered, original deck positions covered) outcomes are feasible on the all-filler observation branch:

| a Arc / s Shoes | Efficient coverage pairs (Prize, deck) |
|---|---|
| 0/4 | (3, 8) |
| 1/3 | (3, 7), (4, 6) |
| 2/2 | (4, 5), (5, 4) |
| 3/1 | (5, 3), (6, 2) |
| 4/0 | (6, 1) |

Both outcomes for mixed a=1..3 have concrete legal witness schedules.

**Deck-heavy:** First play all Shoes, probing two successive original deck positions per Shoes. Then Arc1 inspects the next deck top and swaps in an unknown Prize. Later Arcs serially inspect previously swapped Prize identities. Peonia checks three remaining Prize positions. This covers (a+2, 9-2a).

**Prize-heavy:** Use the Arcs first, beginning with an inspection of original deck top and exchanging with an unknown Prize. The final Arc leaves a Prize identity on top. Shoes1 takes that Prize if it is T; otherwise it discards the filler and draws the next original deck card. Remaining Shoes each see two more original deck positions, and Peonia checks three remaining Prize slots. This covers (a+3, 8-2a).

The observation-count cap is \`3+a+2s=11-a\`. Separate zone limits are \`3+a\` Prize slots and \`1+2s=9-2a\` deck positions for a>=1,s>=1. These caps eliminate any pair strictly beyond the displayed Pareto frontiers. Every target location in a covered set is recoverable by adapting only to actual observations.

The two efficient options within a given mixed inventory trade one Prize position for one deck position. The prize-heavy choice becomes better when

\`p/6 > (1-p)/46\`, i.e. \`p > 3/26\`.

Across the four prize-heavy mixes a=0..3, adding one Arc while removing one Shoes gains one Prize position but loses two deck positions. Its gain becomes positive when

\`p/6 > 2(1-p)/46\`, i.e. \`p > 6/29\`.

Below that threshold, the four-Shoes mix dominates the other feasible pairs. Above it, the 3/1 mix dominates. The 4/0 mix is dominated by 3/1 except at p=1.

## Adaptive verification

\`tools/arc_peonia_mixed_prior.py\` implements an independent exact \`Fraction\` Bellman search over target physical positions, preserving *starting-zone identity* after swaps and deck removal so posterior weights remain correct. It permits all Item orderings and each look-then-choice rule. Comparisons cover 21 evenly spaced prior values from 0 through 1, both structural breakpoints \`3/26\` and \`6/29\`, and points directly on either side of the global threshold.

The solver agrees with every closed-form fixed-mix bound on all **125** rational configurations. At p=6/29 it returns the predicted four-way tie \`7/29\`. The Windows CI regression runs the same exact test.

## Strategic interpretation and limits

The switch is a clean mathematical example of matchup/state-dependent resource allocation. Arc Phone's ability to serially reveal Prize cards is most useful when the relevant target is likely Prized. Shoes' access to successive deck cards matters more when the target is likely in the deck.

The experiment holds Peonia, four Items and the replacement payment **already available**; it ignores their access probability, Basic opener requirements, other card values, lock effects, recovery, Supporter opportunity cost, and game outcomes. Its prior p is assumed externally known. The threshold is therefore a model-specific decision boundary, not a universal card-deck-building cutoff.

Future investigation: derive p from actual observable deck-search and opening states, then condition the item-inventory mix on realistic Prize allocation and acquisition costs.
