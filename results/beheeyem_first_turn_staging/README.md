# First-turn board staging for a renewable Beheeyem lock

## Research question

The [alternating Elgyem pipeline](../beheeyem_lock_recycling/) needs two Elgyem and a lock-anchor Basic already on the field before the repeated ordinary evolution sequence begins. Compare the **first-turn card-access geometry** of Battle VIP Pass \`swsh8-225\` and Nest Ball \`sv1-181\` for staging that board.

The target board has:

- one Elgyem placed Active from the opening seven cards;
- one additional Elgyem on the Bench by the end of the first own turn;
- one partner Basic, such as Lillipup for a later Stoutland lock, on the Bench by that deadline.

This is a substrate for the future lock pipeline. It is not the complete turn-two attack setup and does not guarantee evolution, Energy, Stadium, Tool, or lock-anchor completion.

## Relevant exact cards

Battle VIP Pass \`swsh8-225\`: playable only during the player's first turn; searches up to **two Basic Pokémon** and puts them directly onto the Bench.

Nest Ball \`sv1-181\`: searches **one Basic Pokémon** directly onto the Bench and remains playable on later turns.

Both are Items, so the current-state ability to play Items and Bench capacity matter. The comparison assumes no Item lock and enough Bench spaces for the two target Basics.

## Model

A randomized 60-card deck contains four Elgyem, four partner Basics, V Battle VIP Pass, N Nest Ball, and \`52-V-N\` unspecified other cards. Each Item name has at most four copies. The opening hand contains seven cards, followed by six random Prize cards, then one natural draw on turn one.

Demand: Elgyem in the opening seven and, by end of turn one, **two Elgyem in play and one partner Basic in play**. An Item is usable if drawn in the opening seven or turn-one natural draw. Each VIP copy may fetch two missing Basics; each Nest Ball copy may fetch one. Only post-Prize deck copies are available to search.

The enumerator weighs:

1. all multivariate hypergeometric seven-card hands;
2. one ordered natural draw from the 53 remaining cards;
3. all compatible six-Prize configurations from the 52 other cards, using exact hypergeometric multiplicities for Elgyem and partner Basic;
4. available search capacity versus missing Basic demand and unprized target supply.

Sampling the one natural draw before assigning the six Prizes is distribution-equivalent to the actual Prize-then-draw order when all unseen cards are randomly permuted. Prize supply is still checked before resolving searches.

## Exact results

| Battle VIP Pass copies | Nest Ball copies | First-turn ready board |
| ---: | ---: | ---: |
| 0 | 0 | 3.034427% |
| 1 | 0 | 7.586977% |
| 0 | 1 | 5.125785% |
| 4 | 0 | 18.483546% |
| 0 | 4 | 11.775394% |
| 2 | 2 | 15.129470% |
| 4 | 4 | 24.168324% |

With four of either Item, Battle VIP Pass has a **6.708152-percentage-point advantage** over Nest Ball for this specific two-Basic first-turn staging demand. Its extra output capacity matters when the opening hand has one Elgyem but lacks both the second Elgyem and the lock-anchor Basic.

The advantage changes with the objective's time horizon. VIP becomes unplayable after the first turn, whereas Nest Ball can search a recycled Elgyem from the deck on subsequent turns. Optimizing solely for this staging endpoint risks removing later-turn retrieval capacity that the Beheeyem cycling line depends on.

## Validation

The reproducer conserves the full exact probability space, checking the sum over seven-card hands, one natural draw, and six Prizes equals \`C(60,7) * 53 * C(52,6)\`. All probabilities are exact rational counts rounded to six decimals.

Independent 300,000-trial simulations with random Prize placement (seed 20261009) returned 18.535667% for four VIP and 11.846667% for four Nest, within sampling error of the exact 18.483546% and 11.775394%.

Run: \`python results/beheeyem_first_turn_staging/reproduce.py\`.

## Limitations and suggested extension

The model intentionally excludes other Basic Pokémon starts, mulligan bonus draws, search into Items, extra turn-one draws, opposing interference, whether the desired anchor can evolve by turn two, and the subsequent search-card depletion loop. The figures measure one precise time-gated ready-board event, not complete lock probability or metagame performance.

The strategic issue is **staging versus maintenance**. First-turn VIP is a high-capacity connector with a firm expiration deadline, while Nest Ball has smaller immediate capacity and retains later usefulness. A stronger finite-horizon deck optimizer should value both the initial staging event and the ability to recover the shuffled Elgyem on each successive turn, with consumed Item copies tracked across turns.
