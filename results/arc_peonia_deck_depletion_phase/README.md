# Optimal Arc Phone / Trekking Shoes allocation across deck depletion

## Question

Suppose there is one single-copy critical card T, known to be uniformly located among the six face-down Prizes and the d remaining deck cards, but its zone is not yet established (a uniform K0-like hidden-location posterior). You hold Peonia, replacement filler payment, and four usable Items in some mix of Arc Phone and Trekking Shoes. How should the mix change as the deck becomes smaller?

All cards other than T are inert filler for this isolated experiment. Item and Supporter effects use their actual order of observations and legal one-per-turn Supporter capacity.

## Exact six-Prize phase diagram

Let a be Arc Phone copies; the other 4-a Items are Trekking Shoes. The best mix is determined by maximizing the number of initial target positions from which an adaptive policy can put T into hand:

| Unknown deck positions d | Best number of Arc Phone a | Corresponding Shoes | Optimal T retrieval probability |
|---:|---|---|---|
| 1 | 3 or 4 | 1 or 0 | 7/7 = 100% |
| 2 | 3 | 1 | 8/8 = 100% |
| 3 | 2 or 3 | 2 or 1 | 8/9 = 88.8889% |
| 4 | 2 | 2 | 9/10 = 90% |
| 5 | 1 or 2 | 3 or 2 | 9/11 = 81.8182% |
| 6 | 1 | 3 | 10/12 = 83.3333% |
| 7 | 0 or 1 | 4 or 3 | 10/13 = 76.9231% |
| 8 and above | 0 | 4 | 11/(6+d) |

The optimal number of Arc Phone copies decreases as the hidden deck grows. Every odd-sized intermediate deck in d=1,3,5,7 has a tie between adjacent inventories, while d=2,4,6 have a unique mixed optimum.

The optimal *probability itself* need not decrease monotonically when d increases: d=3 gives 8/9, d=4 gives 9/10, because adding one remaining deck slot makes an additional plan feasible and increases the number of covered locations from eight to nine. Likewise d=5 gives 9/11, d=6 gives 10/12.

## Physical acquisition mechanism

Arc Phone (\`swsh11-152\`) can move a hidden Prize card to the deck top and a later Arc Phone can observe it. Trekking Shoes (\`swsh10-156\`) can choose to take the observed deck top or discard it and draw the next card. Peonia (\`swsh6-149\`) can select up to three Prize cards and replace them from the hand.

The closed-form exact coverage of an initial uniform T position is given in [the K0 frontier](../arc_peonia_k0_item_frontier/):

- With a=0: \`C=min(6,3)+min(d,2s)\`.
- With a>=1: \`C=min(6+d, 3+a+2s, min(6,a+2+1_{s>0})+min(d,1+2s))\`.

The success probability is \`C/(6+d)\`. Substitute \`s=4-a\` and compare a=0,1,2,3,4. For d>=8, four Shoes can cover eleven distinct original T locations: three Prize slots through Peonia and eight successive deck slots through conditional Shoes operations. Other four-Item mixes cover at most ten.

When d is small, the fourth Shoes' second-card and later deck probes run out of remaining cards, while more Arc Phone can reach additional Prize slots. That finite deck saturation shifts the efficient resource allocation.

## Reproduction and limitations

\`tools/arc_peonia_deck_depletion_phase.py\` checks all 46 deck sizes d=1..46 and asserts the exact optimal inventory for each. It independently runs the full observable physical-world policy solver on all five inventories at d=1..12 and d=46: **65 exact adaptive-policy checks**. Run \`python tools/arc_peonia_deck_depletion_phase.py\` or use the Windows CI workflow.

This is conditional on already holding the Item package, Peonia and feasible replacement payment, no action costs or other relevant cards, and a uniform unknown T location. When the deck is searched and its contents become known (K1), a different posterior and therefore a different optimum can result. The findings describe exact target recovery under a simplified subsystem and should not be read as real turn-level probabilities or deck-construction recommendations.

Next: add a stopping hazard for deck-out on the following turn and a realistic opportunity cost per Shoes, then test whether the discontinuous deck-size boundaries persist when target retrieval must lead to a legal attack.
