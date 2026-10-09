# Arc Phone and Trekking Shoes: adaptive Item feedback across Prize positions

## Question

Do Items retrieved from Prize cards during a sequence of Arc Phone swaps materially change the reachable line, and when does the player need to spend an Item merely to observe the currently hidden deck top?

Both effects matter. The previous [Arc Phone chain availability study](../arc_phone_chain_access/) deliberately restricted Item retrieval to the initial hand and Peonia pickups. This result adds a finite-horizon belief-state policy that may retrieve **Arc Phone** and **Trekking Shoes** cards exposed by intermediate swaps.

Source card texts: [official Arc Phone](https://asia.pokemon-card.com/sg/card-search/detail/2749/), [official Trekking Shoes](https://asia.pokemon-card.com/sg/card-search/detail/3614/). Arc Phone looks at top before an optional face-down Prize exchange; Trekking Shoes looks at top and can take it into hand. The legality-coded source prints are `swsh11-152` and `swsh10-156`.

## Exact transition model

Implementation: `tools/arc_phone_feedback_policy.py`. Independent validation: `results/arc_phone_feedback_policy/reproduce.py`.

A joint posterior has physical Prize-slot identities and the current deck-top identity. Groups are `T` (target singleton), `A` (Arc Phone), `S` (Trekking Shoes), and `F` (neutral filler). The starting Prize composition is known, while physical positions are uniformly unknown; all slots are face down. The initial top is known `F`.

On an Arc Phone action, the player must commit an `A` from hand. That action observes the top card, then chooses any one Prize position to exchange with it **or declines the exchange**. The outgoing Prize card becomes the new unknown deck top until observed through a later Item.

On a Trekking Shoes action, the player commits an `S` and observes the top. A `T` is taken into hand for immediate success; an `A` or `S` is taken into hand and becomes usable. A neutral `F` has no strategic value in this model. After an intervening Shoes draw, the next deck top is assumed known neutral `F`; this is a controlled-deck counterfactual that omits other card draw and limits.

The exact Bellman policy chooses whether to play Arc Phone or Trekking Shoes **before** observing the top through that action, then chooses the Arc destination after the observation. It can stop on a target hit. Every Item play consumes a physical Item copy, so the recursion terminates.

## Results

All probabilities condition on the target starting in the listed unknown Prize positions and the specified Items already being in hand. They are exact fractions over physical Prize permutations.

| Prize composition | Initially accessible Items | Adaptive optimum | Always alternate Arc → Shoes | No-intermediate-Item-reuse chain |
| --- | --- | ---: | ---: | ---: |
| T, A, S (3 Prizes) | 2 Arc, 1 Shoes | 2/3 = 66.667% | 1/2 = 50% | 2/3 = 66.667% |
| T, A, S (3 Prizes) | 2 Arc, 2 Shoes | **1 = 100%** | 1 = 100% | 2/3 = 66.667% |
| T, A, S, F (4 Prizes) | 3 Arc, 2 Shoes | **7/8 = 87.500%** | 2/3 = 66.667% | 3/4 = 75% |
| T, A, S, F, F, F (6 Prizes) | 3 Arc, 2 Shoes | **13/24 = 54.167%** | 2/5 = 40% | 1/2 = 50% |

The last three configurations stay within the ordinary four-copy limits for both Item names. The table's last column is a fixed-resource, one-final-Shoes chain that excludes the opportunity to draw newly exposed `A` and `S` copies before the terminal endpoint. The middle comparator always draws immediately after each Arc exchange, instead of deciding adaptively when information or Item recovery justifies that draw.

### Three-Prize guaranteed retrieval

Start with three unknown slots containing exactly `T`, `A`, and `S`, and two Arc Phone plus two Trekking Shoes in hand. Play Arc Phone to swap the neutral deck top with an untested Prize. Use Trekking Shoes to take its outgoing card.

- If it is `T`, the objective is complete.
- If it is `A`, the player replenishes Arc Phone inventory.
- If it is `S`, the player replenishes Trekking Shoes inventory.

Every miss retrieves a card that pays back one of the two Item categories needed to continue. The same Arc → Shoes policy visits another untested slot. Whatever the order of the three Prize identities, it reaches `T` before running out of available Items. The six possible physical permutations are all winning witnesses. A static count of the two initially held Arc Phone cards would incorrectly cap successful slot coverage at two of three.

### Information is valuable only when the right action remains available

For the four-Prize case (`T,A,S,F`, with three Arc Phone and two Shoes), optimal adaptive success is `7/8`.

If the player could observe the outgoing top card **for free immediately after the first Arc Phone swap**, the resulting clairvoyant continuation value would instead be `23/24`. The difference is **`1/12` = 8.333333 percentage points**.

The actual player must first commit to another Arc Phone or a Trekking Shoes before that card is observed. Choosing that observation channel is itself a resource decision. An algorithm that conditions on the outgoing card and only then decides which Item to spend introduces free information that the card texts do not supply.

## Independent validation

The regression implements a second exact dynamic program over explicit labeled physical worlds, retaining duplicate-world multiplicity. Its state and transition representation is independent of the normalized posterior used by the primary solver. Nine scenarios with three, four, and six Prize positions agree as exact `Fraction` values. A separate physical-policy enumerator validates the always-alternating baseline.

## Limits and next work

The model intentionally excludes Peonia, prior look-at-Top effects, deck depletion, optional Shoes discard-and-next-draw mode, search access to Item cards, locks, opponent interference, and downstream value of the card moved into the Prize zone. The neutral filler top after Shoes is an explicit assumption.

A stronger next step should compose the full deck-top posterior with the physical Prize posterior and let Trekking Shoes either keep top or discard it and draw the next actual card. That will require tracking future deck order, connected search resources, and card-specific strategic protection. Until then, these results are exact controlled-state counterexamples to static resource counting, not competitive deck win-rate estimates.
