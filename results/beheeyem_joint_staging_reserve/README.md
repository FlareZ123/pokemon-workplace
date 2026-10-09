# First-turn Beheeyem staging versus reserving a turn-three Nest Ball

## Problem and strategic significance

The [renewable Beheeyem handoff](../beheeyem_lock_recycling/) requires two Elgyem and an eventual lock-anchor Basic to be in play early, but after the first Mysterious Noise the Elgyem that attacked is shuffled into the deck. A player must have a way to retrieve the returned Elgyem on the following own turn to maintain ordinary-evolution tempo.

Battle VIP Pass has high first-turn Basic-search capacity but expires immediately; Nest Ball searches only one Basic at once yet remains live on subsequent turns. Optimizing first-turn board staging alone might consume deck slots that would have supplied the later Nest Ball. This exact experiment measures **both deadlines jointly**.

## Event, assumptions and sequencing

Draw a uniformly random seven-card opening hand from a 60-card deck containing four Elgyem, four partner Basics, V copies of Battle VIP Pass, N copies of Nest Ball, and 52-V-N neutral cards. Put six random Prize cards aside. Draw one card on the first own turn and another at the start of the second own turn. No additional draws, tutoring, mulligan bonuses, recovery, interference, or Supporter effects are permitted.

A first-turn **ready board** requires:

1. An Elgyem in the original opening seven, selected Active.
2. A second Elgyem and a replacement lock-anchor Basic on the Bench by the end of the first own turn.

Each VIP held by that deadline may fetch up to two missing Basics from the post-Prize deck; each Nest held may fetch one. If both can satisfy the demand, the policy uses the minimum number of Nest copies, saving them for later.

The stricter **ready + reserved** event additionally requires at least one unplayed Nest Ball either already in hand after first-turn staging or drawn on the second own turn, available to save until own turn three to Bench the Elgyem recycled by Beheeyem's turn-two attack.

This last event does not itself check turn-two Beheeyem evolution/attack/TAE access, nor whether the lock-anchor can be fully established. It tests a necessary retrieval resource under a specific timing constraint.

## Exact enumeration

The computation enumerates opening-hand category counts, the first natural draw, and random Prize counts for Elgyem, partner Basic and Nest Ball. It rejects cases in which a search cannot find its Prized-out target. After performing the required Basic searches, a remaining Nest Ball can be acquired on turn two only from the **post-search deck**, whose size is \`46 - number_of_searched_Basics\`.

Draw-before-Prize enumeration is combinatorially equivalent to physically placing six random Prizes before the first-turn draw, because all unseen cards have uniformly random relative order. The model explicitly preserves Prize-dependent deck supply.

The script uses integer-weighted combinatorial counts and exact rational arithmetic, with common continuation denominator \`LCM(44,45,46)\`, so no Monte Carlo estimates are used in the result table. The count of all opening hands, first-turn natural draws and Prize arrangements is independently checked against \`C(60,7) × 53 × C(52,6)\`.

## Results: fixed four search-Item slots

| VIP copies | Nest copies | First-turn ready board | Ready board + Nest retained by own turn two |
| ---: | ---: | ---: | ---: |
| 0 | 4 | 11.775394% | 2.757941% |
| 1 | 3 | 13.452432% | **3.181558%** |
| 2 | 2 | 15.129470% | 2.918123% |
| 3 | 1 | 16.806508% | 1.886791% |
| 4 | 0 | **18.483546%** | 0.000000% |

**Rank reversal:** Four VIP Pass maximize the immediate staging endpoint, while one VIP plus three Nest maximize the two-deadline event under these exact four slots and the stated policy.

The nonmonotonic result is a consequence of opportunity cost across time. More VIP copies improve access to both Bench targets on turn one, but reduce the stock of Nest Ball that is meaningful after turn one. An all-VIP search package cannot satisfy the reserved-Nest condition by definition.

An independent 200,000-trial Monte Carlo replay of complete decks, Prize placement, first-turn searches and turn-two draws supports the exact results: for one VIP/three Nest, 13.4435% staging and 3.2140% joint; for two VIP/two Nest, 15.2555% and 2.9560%; for four VIP/zero Nest, 18.4155% and 0%.

## Limitations

- A practical deck can find Nest Ball via other routes, draw more cards, or retrieve recycled Elgyem using different Basic-search effects. This would change the best four-slot package.
- Draws and Items are strategically contextual; the simplified policy only minimizes first-turn Nest consumption given the required two Basics.
- It assumes the original Elgyem is chosen Active from the opening seven, with the partner Basic needing to reach the Bench by the first-turn deadline. Other starts may use switching effects.
- It does not model the competing turn-two need to find Beheeyem, Triple Acceleration Energy, or anchor evolution pieces, which may consume the very same search/draw channels.
- The probability is a raw event over hypothetical 60-card decks. It is neither a matchup success rate nor a fully optimized deck consistency estimate.

## Reproduction and next steps

Run \`python results/beheeyem_joint_staging_reserve/reproduce.py\` to regenerate all values and sample-space conservation assertions.

The next meaningful study should introduce actual multi-turn retrieval paths and score whether they satisfy **both** the first-turn staging constraint and the turn-three recycled-Basic requirement without exhausting Supporter windows or discardable hand resources. This model demonstrates why multi-deadline evaluation can reverse the ranking of card-slot substitutions.
