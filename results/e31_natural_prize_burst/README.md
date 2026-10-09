# Natural Greedy Dice + Dream Ball + Jirachi Prize burst is exceptionally rare

## Question

What is the probability that a shuffled 60-card deck naturally places both singleton Prize-origin Items, Greedy Dice and Dream Ball, in the two Prize slots taken by a supplied two-Prize Knock Out, with a singleton Jirachi Prism Star among the four other Prize slots?

This isolates the *unseeded* situation, separate from the high-information [Peonia placement strategy](../e31_peonia_seed_execution/). With no position knowledge, it also asks for the probability that the Greedy Dice coin lands heads and the player selects Jirachi's unknown physical position as the extra Prize.

Implementation: [tools/e31_natural_prize_burst.py](../../tools/e31_natural_prize_burst.py).  
CI: [passing run 37977335104](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37977335104).

## Controlled random population

The 60-card deck has one Greedy Dice, one Dream Ball, one Jirachi Prism Star, `B` other Basic Pokémon starters and `57-B` inert non-Basic cards.

A normal legal opening consists of seven starting cards containing any Basic Pokémon, followed by six random face-down Prizes. The event considers a hypothetical two-Prize Knock Out where the player selects two of those Prize cards without any additional position knowledge. The Knock Out itself, initial board state, relevant attack and one open Bench slot are supplied, not generated.

The two selected Prize cards must be Greedy Dice and Dream Ball in either order. Jirachi must occupy one of the remaining four face-down Prize positions. That exact three-singleton event has the unconditional probability

`2! * 4 / (60 * 59 * 58) = 8 / 205320`

or approximately `0.0038963569%`.

Jirachi is Basic, but it is Prized in this event and thus cannot be the opening Active. Conditional on three named cards being in their designated Prize positions, a legal starting hand must contain one of the `B` alternative Basics among the seven drawn from the other 57 cards.

## Exact conditional results

| Other Basic starters `B` | Both Items in chosen 2 Prizes and Jirachi among remaining 4, conditional on accepted opening | Four-Prize burst after Greedy heads and Jirachi hit, conditional on accepted opening |
| ---: | ---: | ---: |
| 4 | 0.00342356% | 0.000427945% |
| 8 | 0.00375652% | 0.000469564% |
| 12 | 0.00385541% | 0.000481926% |
| 16 | 0.00388957% | 0.000486196% |

For `B=8`, the exact four-Prize-burst probability conditional on an accepted opening is

`14873771 / 3167567907660 = 0.00046956439241701393%`,

approximately one in **212,963 accepted openings**.

This is a hypothetical first two-Prize award from **six** initial Prizes, so taking four Prizes in this event leaves two remaining. It is a **four-Prize burst**, without claiming that the game is immediately won.

The conditional natural event probability is `29747542/791891976915` for `B=8`. Its Greedy-on-heads/Jirachi-hit branch is smaller by a factor of eight.

## Probability derivation

Let `E` mean that Greedy Dice and Dream Ball occupy the chosen two Prize slots, in either order, and Jirachi occupies one of the four other Prize slots. Then

`P(E) = 2 * 4 / (60 * 59 * 58)`.

Let `L` mean that the opening seven contain at least one Basic. The deck has `B+1` Basics including Jirachi:

`P(L) = 1 - C(59-B,7)/C(60,7)`.

Conditional on `E`, Jirachi is Prized and the opening seven are drawn from the 57 other cards, only `B` of which are Basic:

`P(L|E) = 1 - C(57-B,7)/C(57,7)`.

Bayes' rule then gives

`P(E|L) = P(E) * P(L|E)/P(L)`.

To additionally trigger Jirachi from Greedy Dice's extra Prize requires a heads result (probability `1/2`) and choosing its face-down position among four exchangeable remaining slots (probability `1/4`). Thus

`P(four-Prize burst|L) = P(E|L)/8`.

All calculations are exact rational arithmetic. The executable checks the direct accepted-hand count against the conditional calculation and asserts the resulting exact ratios for multiple Basic counts.

## Implication

This is an intentionally stringent, unassisted baseline. A state where both Prize-origin Items are awarded together and Jirachi remains Prized is possible, but an engine should never assume such states appear frequently without conditioning on the card-access and Prize-placement process that creates them.

It would be incorrect to combine the natural-Prize probabilities here with the known-position advantage from Peonia as independent events. Peonia deliberately changes which cards are in each Prize position, and it has its own hand-access requirements. The two experiments describe distinct data-generating processes.

Deck searches, Peonia replacement, special Prize effects, prior Prize awards, and additional Pokémon copies would require their own conditional models.

## Reproduction

`python tools/e31_natural_prize_burst.py`.
